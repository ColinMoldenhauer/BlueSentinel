# Packages:
import datetime
import os
from pathlib import Path

from fastkml import kml
from shapely.geometry import box

import geopandas as gpd
import fiona
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as colors
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.lines import Line2D
import matplotlib.patches as patches
import json
import numpy as np
import scipy.stats as stats
from shapely.geometry import MultiPolygon, Polygon, box, shape
import rioxarray  # noqa: F401 # Its necesary for xarray.open_mfdataset() with engine `rasterio`
import xarray as xr  # It may need Dask library https://docs.dask.org/en/stable/install.html


from sentinelhub import (
    CRS,
    BBox,
    BBoxSplitter,
    bbox_to_dimensions,
    CustomGridSplitter,
    DataCollection,
    MimeType,
    MosaickingOrder,
    OsmSplitter,
    SentinelHubDownloadClient,
    SentinelHubRequest,
    TileSplitter,
    UtmGridSplitter,
    UtmZoneSplitter,
    read_data,
)

from sentinelhub import SHConfig



# Request API access:
config = SHConfig()
config.sh_client_id = '428a0042-c613-4c7d-bca8-dbe6f31fb6fe'
config.sh_client_secret = 'CMBkRfCG1WGXr4LQkQ6ZE7WW5enKNs1qDBgm6a9l'
config.save()

#%% API Requests:

evalscript_all_bands = """//VERSION=3
function setup() {
  return {
    input: ["VH", "dataMask"],
    output: [
      { id: "default", bands: 4 },
      { id: "eobrowserStats", bands: 1 },
      { id: "dataMask", bands: 1 },
    ],
  };
}

function evaluatePixel(samples) {
  const value = Math.max(0, Math.log(samples.VH) * 0.21714724095 + 1);

  return {
    default: [value, value, value, samples.dataMask],
    eobrowserStats: [(10 * Math.log(samples.VH)) / Math.LN10],
    dataMask: [samples.dataMask],
  };
}

// ---
/*
// displays VH in decibels from -20 to 0
// the following is simplified below
// var log = 10 * Math.log(VH) / Math.LN10;
// var val = Math.max(0, (log + 20) / 20);

return [Math.max(0, Math.log(VH) * 0.21714724095 + 1)];
*/
"""

# Vers. 2:
# """
#     //VERSION=3
#     function setup() {
#         return {
#             input: [{
#                 bands: ["HV"],
#             }],
#             output: {
#                 bands: 1,
#             }
#         };
#     }

#     function evaluatePixel(sample) {
#         return [sample.HV];
#     }
# """



def request_sentinel1(bbox, time_interval):
    return SentinelHubRequest(
        evalscript=evalscript_all_bands,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL1_IW,
                identifier="S1GRD",                             # has to match Sentinel 1 input datasource id in evalscript
                time_interval=time_interval,
            )     
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=bbox,
        size=bbox_to_dimensions(bbox, resolution=10),
        data_folder="tempfile",
        config=config,
    )




# Bboxes AOI:
coords_baie_de_seine_occidentale = [-1.28905462, 49.38488672, -0.90260433, 49.60361061] #2020
coords_baie_de_seine_orientale = [-0.33333354, 49.29219742,  0.07195561, 49.45000049]   #2021
coords_bancs_des_flandres = [ 1.78058555, 51.039541,  2.53668138, 51.31272003]        #2002

# Create a Bbox from AOI
bbox_AOI = BBox(coords_bancs_des_flandres, CRS.WGS84)  
bbox_size = bbox_to_dimensions(bbox_AOI, resolution=10)

print(f"Image shape at 10 m resolution: {bbox_size} pixels")



# Create a splitter to obtain a list of bboxes with ca 10km sides
region_shape = shape(bbox_AOI)
bbox_splitter = BBoxSplitter([region_shape], CRS.WGS84, (2,2))  # bounding box will be split into grid of 2x2 bounding boxes
show_splitter(bbox_splitter)

print("Area bounding box: {}\n".format(bbox_splitter.get_area_bbox().__repr__()))

bbox_list = bbox_splitter.get_bbox_list()
info_list = bbox_splitter.get_info_list()



time_interval = '2023-11-04'     # YY-MM-DD
sar_image = request_sentinel1(bbox_AOI,time_interval).get_data()

plt.imshow(sar_image)





