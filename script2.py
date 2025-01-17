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
from datetime import date

#aoi_bounds = (3.875107329166124, 43.48641456618909, 4.118824575734205, 43.71739887308995)
aoi_bounds = [2.4, 46.85, 2.6, 47.85]


# retrieving the relevant STAC Item
catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
    )

today = date.today()
last_month = today.replace(month=today.month-1).strftime('%Y-%m')
time_range = f"2018-01-01/2018-12-31"
search = catalog.search(
    collections=['sentinel-2-l2a'],
    datetime=time_range,
    bbox=aoi_bounds,
    query={
                    #'eo:cloud_cover': {"lt": 100}, 
                    #'s2:nodata_pixel_percentage': {'lt': 50},
                    #'s2:mgrs_tile': {'eq': '30PVT'}},
                    's2:mgrs_tile': {'eq': '31TDN'}}
)
items = search.item_collection()
print(f"{len(items)} items found")

bands = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B11', 'B12']
FILL_VALUE = 2**16-1
array = stackstac.stack(
                    items,
                    #assets = bands,
                    resolution=10,
                    dtype="uint16",
                    fill_value=FILL_VALUE,
                    bounds_latlon=aoi_bounds,
                    )
print(array.band)