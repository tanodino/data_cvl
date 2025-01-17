import geopandas as gpd
import pystac_client
import stackstac
import planetary_computer
import xarray as xr
import numpy as np
import pandas as pd
import rioxarray
from tqdm import tqdm
import warnings
import os
import sys
from shapely.geometry import Polygon


#1


def createGeoJson(long_min, lat_min, long_max, lat_max, year):
    # Define the coordinates for the polygon
    #coordinates = [(2.4, 47.4), (2.7, 47.4), (2.7, 47.5), (2.4, 47.5)]
    coordinates = [(long_min, lat_min), (long_max, lat_min), (long_max, lat_max), (long_min, lat_max)]
    # Create a Polygon geometry
    polygon_geom = Polygon(coordinates)

    # Create a GeoDataFrame with a single row and the Polygon geometry
    gdf = gpd.GeoDataFrame(geometry=[polygon_geom])

    # Define the output GeoJSON file path
    output_geojson = 'output_polygon_%s.geojson'%year

    # Save the GeoDataFrame to a GeoJSON file
    gdf.to_file(output_geojson, driver='GeoJSON')



# geometry_path = './Koumbia_db/Koumbia_JECAM_2018-20-21.shp'
# bands = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B11', 'B12']
# year = '2018'

def extract_ts(geometry_path, bands, year, subset, output_path, long_min, lat_min, long_max, lat_max, mgrs_tile):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    #aoi = gpd.read_file(geometry_path)
    #aoi_4326 = aoi.to_crs('EPSG: 4326')
    #bbox = aoi.total_bounds
    #print(bbox)
    #bbox = [2, 47, 2.7, 47.5]
    bbox = [long_min, lat_min, long_max, lat_max]
    #print(bbox)
    createGeoJson(long_min, lat_min, long_max, lat_max, year)
    
    bands = bands
    year = year
    
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
        )


    date_time = year + '-01-01/' + year + '-12-31'
    #print(date_time)
    search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox= bbox,
            datetime= date_time,
            query={
                    #'eo:cloud_cover': {"lt": 100}, 
                    's2:nodata_pixel_percentage': {'lt': 50},
                    #'s2:mgrs_tile': {'eq': '30PVT'}},
                    #'s2:mgrs_tile': {'eq': '31TDN'}}
                    's2:mgrs_tile': {'eq': mgrs_tile}}
                    
            )
    
    items = search.item_collection()
    
    time_steps_pc = len(items)
    print(time_steps_pc)    
    FILL_VALUE = 2**16-1
    #stack = stackstac.stack(item, resolution = 10, bounds = bbox, chunksize= (time_steps_pc, 1, 'auto', 'auto'), xy_coords= 'center')
    stack = stackstac.stack(items, resolution=10, dtype="uint16", fill_value=FILL_VALUE, bounds_latlon = bbox)

    stack = stack.drop_duplicates(dim = 'time')
    print(stack)
    

    SCL = stack.sel(band = 'SCL')
    nodatapixel = xr.where(SCL == 0, 1, 0) # NO DATA, binary mask 0, 1
    saturated = xr.where(SCL == 1, 1, 0) # saturated pixels, binary mask 0, 1
    shaclouds = xr.where(SCL == 3, 1, 0) # Cloud shadows, binary mask 0, 1
    unclass = xr.where(SCL == 7, 1, 0) # unclassified pixels, binary mask 0, 1
    medclouds = xr.where(SCL == 8, 1, 0) # Medium probability clouds, binary mask 0, 1
    highclouds = xr.where(SCL == 9, 1, 0) # High probability clouds, binary mask 0, 1
    cirrus = xr.where(SCL == 10, 1, 0) # cirrus pixels, binary mask 0, 1

    mask = highclouds + medclouds + shaclouds + saturated + cirrus + unclass + nodatapixel # Mask, binary mask 0, 1
    
    stack = stack.sel(band = bands)
    maskedstack = stack.where(mask == 0, np.nan)
    
    print('Masking collection complete')
    
    corr = 5 - maskedstack.time.dt.dayofyear.values[0]
    pc_idx = (maskedstack.time.dt.dayofyear.values + corr) / 5
    missing_idx = np.setdiff1d(np.arange(5, 370, 5) / 5, pc_idx)
    n_missing = missing_idx.shape[0]

    for band in bands:#tqdm(bands):
        print('Starting loading band: {}'.format(band))
        pcdata = np.array(maskedstack.sel(band = band).values)
        sys.stdout.flush()
    
        print('Loading band {} into memory complete'.format(band))
        print('numpy data with size ',pcdata.shape)
        sys.stdout.flush()

        n_y = pcdata.shape[1]
        n_x = pcdata.shape[2]
        nandata = np.array([np.nan]*n_missing*n_y*n_x).reshape(n_missing, n_y, n_x)
        completets = np.zeros((73, n_y, n_x))
        
        for n, i in enumerate(pc_idx):
            completets[int(i)-1, :, :] = pcdata[n, :, :]
        
        for n, i in enumerate(missing_idx):
            completets[int(i)-1, :, :] = nandata[n, :, :]
        
        print('Band: {} - Complete TS in numpy'.format(band))
        sys.stdout.flush()

        x = maskedstack.indexes['x']
        y = maskedstack.indexes['y']
        dates = [pd.to_datetime(doy-1, unit='D', origin=str(year)) for doy in np.arange(5, 370, 5)]
        time = pd.Index(dates, name = 'time')
    
        completets = xr.DataArray(
            data = completets,
            coords=dict(time = time,
                        y = y,
                        x = x)
            )
        completets._copy_attrs_from(maskedstack)
    
        print('Band: {} - Complete TS in DataArray'.format(band))
        sys.stdout.flush()
        interpolated = completets.interpolate_na(dim="time", method="linear", use_coordinate = 'time')
        interpolated = interpolated.ffill(dim= 'time')
        interpolated.data = interpolated.data.astype(np.uint16)
        print('Band: {} - Interpolation complete'.format(band))
        sys.stdout.flush()
        # minmax_bandtime = interpolated.quantile([0.02, 0.98], dim=['x', 'y'])
        # normalized = (interpolated - minmax_bandtime[0, :, :]) / (minmax_bandtime[1, :, :] - minmax_bandtime[0, :, :])
        # normalized = normalized.where(normalized > 0, 0, drop=True)
        # normalized = normalized.where(normalized < 1, 1, drop=True)
    
        print('Band: {} - Starting writing tif file'.format(band))
        sys.stdout.flush()
        interpolated.rio.to_raster("{}s2_{}_{}.tif".format(output_path, year, band))
    
    
if __name__ == "__main__":
    # parse arguments
    import argparse
    from argparse import RawTextHelpFormatter

    parser = argparse.ArgumentParser(
        description="Preprocess and write Sentinel 2 images time series",
        formatter_class=RawTextHelpFormatter,
    )


    parser.add_argument(
        "--geometry_path",
        type=str,
        #default='/home/edgar/DATA/Koumbia_db/Koumbia_JECAM_2018-20-21.shp',
        default='/home/dino/DATA/data_cvl/shapefile_Centre_Val_de_Loire/cvl.shp'
    )
    
    parser.add_argument(
        "--bands",
        type=list,
        #['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B11', 'B12']
        default=['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B11', 'B12'],
    )
    
    parser.add_argument(
        "--year",
        type=str,
        default='2018',
    )
    
    parser.add_argument(
        "--subset",
        type=str,
        default='yes',
    )
    
    parser.add_argument(
        "--output_path",
        type=str,
        #default='/home/edgar/DATA/testimages/',
        default='/home/dino/DATA/data_cvl/shapefile_Centre_Val_de_Loire/testimages/'
    )

    parser.add_argument(
        "--long_min",
        type=float
        #default='/home/edgar/DATA/Koumbia_db/Koumbia_JECAM_2018-20-21.shp',
        #default='/home/dino/DATA/data_cvl/shapefile_Centre_Val_de_Loire/cvl.shp'
    )

    parser.add_argument(
        "--lat_min",
        type=float
        #default='/home/edgar/DATA/Koumbia_db/Koumbia_JECAM_2018-20-21.shp',
        #default='/home/dino/DATA/data_cvl/shapefile_Centre_Val_de_Loire/cvl.shp'
    )

    parser.add_argument(
        "--long_max",
        type=float
        #default='/home/edgar/DATA/Koumbia_db/Koumbia_JECAM_2018-20-21.shp',
        #default='/home/dino/DATA/data_cvl/shapefile_Centre_Val_de_Loire/cvl.shp'
    )

    parser.add_argument(
        "--lat_max",
        type=float
        #default='/home/edgar/DATA/Koumbia_db/Koumbia_JECAM_2018-20-21.shp',
        #default='/home/dino/DATA/data_cvl/shapefile_Centre_Val_de_Loire/cvl.shp'
    )

    parser.add_argument(
        "--mgrs_tile",
        type=str
        #default='/home/edgar/DATA/Koumbia_db/Koumbia_JECAM_2018-20-21.shp',
        #default='/home/dino/DATA/data_cvl/shapefile_Centre_Val_de_Loire/cvl.shp'
    )

    
    config = vars(parser.parse_args())

    
    # Write Sentinel 2 images
    api_key = 'd051c2667c514174bc2ddd4ebce954d3'
    os.environ['PC_SDK_SUBSCRIPTION_KEY'] = api_key

    #long_min = 2.4
    #lat_min = 47.4
    #long_max = 2.7
    #lat_max = 47.5

    #--long_min 1.84   --lat_min  46.5   --long_max 2.0  --lat_max 46.8 --mgrs_tile 31TDM --output_path /home/dino/DATA/data_cvl/shapefile_Centre_Val_de_Loire/S2data_V2/
    extract_ts(**config)