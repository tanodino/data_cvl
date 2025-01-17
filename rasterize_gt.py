import geopandas as gpd
from shapely.geometry import Point
import sys
import numpy as np
import rasterio as rio
from rasterio import features

#4

def overwriteRaster(gdf, template_raster, output_raster):
    template_ds = rio.open(template_raster)
    template_meta = template_ds.meta.copy()
    with rio.open(output_raster, 'w+', **template_meta) as out:
        out_arr = out.read(1)
        shapes = ((geom,value) for geom, value in zip(gdf.geometry, gdf.iloc[:,1]))
        burned = features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform)
        out.write_band(1, burned)

new_epsg = "32631"
year = int(sys.argv[1])

prefix_path = "GT_%d_spatioTemporal"%year
#raster_template = "GT_%d/template.tif"%year
#raster_gt_clid = "GT_%d/gt_clID.tif"%year
#raster_gt_pid = "GT_%d/gt_pID.tif"%year

raster_template = prefix_path+"/template.tif"
raster_gt_clid = prefix_path+"/gt_clID.tif"
raster_gt_pid = prefix_path+"/gt_pID.tif"




gdf = gpd.read_file(prefix_path+"/gt.shp")
gdf = gdf.to_crs(new_epsg)

# Add an incremental ID column to the GeoDataFrame
gdf['incr_id'] = gdf.reset_index().index + 1

gdf_clid = gdf[["geometry","CODE_GROUP"]]
gdf_clid['CODE_GROUP'] = gdf_clid['CODE_GROUP'].astype('int64')
#gdf_clid["CODE_GROUP"] = gpd.to_numeric(gdf_clid['CODE_GROUP'], downcast='integer')
overwriteRaster(gdf_clid, raster_template, raster_gt_clid)

gdf_pid = gdf[["geometry","incr_id"]]
gdf_pid['incr_id'] = gdf_pid['incr_id'].astype('int64')
#gdf_pid["CODE_GROUP"] = gpd.to_numeric(gdf_pid['CODE_GROUP'], downcast='integer')
overwriteRaster(gdf_pid, raster_template, raster_gt_pid)



