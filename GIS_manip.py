import geopandas as gpd
import os
import sys
import numpy as np

#2

def main(shared_crs, shapefile_path, geojson_path, output_path, output_fileName):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # Path to the shapefile and GeoJSON file

    # Read the shapefile and GeoJSON file into GeoDataFrames
    shapefile_gdf = gpd.read_file(shapefile_path)
    geojson_gdf = gpd.read_file(geojson_path)

    #reproject geometry in the same CRS
    shapefile_gdf = shapefile_gdf.to_crs(shared_crs)
    geojson_gdf = geojson_gdf.to_crs(shared_crs)



    # Perform the spatial intersection
    intersection_gdf = gpd.overlay(shapefile_gdf, geojson_gdf, keep_geom_type=True, how='intersection')
    #intersection_gdf = intersection_gdf.to_crs("32631")
    #print(intersection_gdf)

    # Perform negative buffer
    negative_buffer_distance = -10
    intersection_gdf['geometry'] = intersection_gdf.buffer(negative_buffer_distance)
    vals = intersection_gdf.area.to_numpy()
    #print( np.bincount( np.isnan(vals).astype("int")) )
    #exit()


    #invalid_geometries = intersection_gdf[~intersection_gdf['geometry'].is_valid]
    print( intersection_gdf.shape[0] )
    intersection_gdf = intersection_gdf[intersection_gdf.is_valid]
    print( intersection_gdf.shape[0] )


    # Save the result to a new shapefile
    #output_shapefile = 'GT_2021.shp'
    intersection_gdf.to_file(output_path+"/"+output_fileName)
    #intersection_gdf.to_file("prova.json", driver='GeoJSON')
    
    temp_gdf = gpd.read_file(output_path+"/"+output_fileName)
    temp_gdf = temp_gdf[temp_gdf.is_valid]
    temp_gdf.to_file(output_path+"/"+output_fileName)


    print(f'Intersection result saved to {output_path+"/"+output_fileName}')


if __name__ == "__main__":
    shared_crs = "2154"

    
    # DATA QUENTIN
    shapefile_path = 'data_quentin/parcels_loire.shp'
    geojson_path = 'output_polygon_2021.geojson'
    output_path = "GT_2021_spatioTemporal"
    output_fileName = "gt.shp"
    main(shared_crs, shapefile_path, geojson_path, output_path, output_fileName)

    

    # DATA EUROCROP
    shapefile_path = '../EuroCrops/FR_2018/FR_2018_EC21.shp'
    geojson_path = 'output_polygon_2018.geojson'
    output_path = "GT_2018_spatioTemporal"
    output_fileName = "gt.shp"
    main(shared_crs, shapefile_path, geojson_path, output_path, output_fileName)
    '''
    '''