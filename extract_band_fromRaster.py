import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window
import sys

#3

year = int( sys.argv[1] )

# Replace 'input_raster.tif' and 'output_band1.tif' with your file paths
input_raster_path = sys.argv[2] #"shapefile_Centre_Val_de_Loire/testimages/s2_%d_B02.tif"%year
output_raster_folder = sys.argv[3]

output_raster_path = output_raster_folder+"/template.tif"

# Open the input GeoTIFF file
src = rasterio.open(input_raster_path)

# Read a specific band (replace '1' with the band number you want)
band_number = 1
band_data = src.read(band_number)

# Get metadata from the source raster
meta = src.meta.copy()

# Update metadata for the new raster
meta['count'] = 1
#meta.update(count=1)  # Number of bands in the new raster
#meta.pop('transform', None)  # Remove the transformation to avoid spatial issues
#meta.pop('tiled', None)  # Remove 'tiled' metadata
src.close()
dst = rasterio.open(output_raster_path, 'w', **meta)
# Write the band data to the new raster
dst.write(band_data, 1)  # Use '1' as the band index

print(f'Band {band_number} extracted and saved to {output_raster_path}')