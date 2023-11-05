import streamlit as st
import numpy as np

import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import os
from sentinelhub import CRS, BBox, MimeType, SentinelHubRequest, SHConfig
from sentinelhub import (
    CRS,
    BBox,
    DataCollection,
    DownloadRequest,
    MimeType,
    MosaickingOrder,
    SentinelHubDownloadClient,
    SentinelHubRequest,
    bbox_to_dimensions,
)
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import cv2
from datetime import datetime, timedelta

st.set_page_config(page_title='Blue Sentinel', page_icon='🐟', layout="centered", initial_sidebar_state="expanded", menu_items=None)
st.sidebar.image('ims/Copernicus_logo.png', width=300)
st.sidebar.image('ims/Environmental_Justice_Foundation_logo.png', width=150)
#st.sidebar.image('images/copernicus-logo_1.svg', width=300)
#st.sidebar.image(os.path.join('images', 'Environmental_Justice_Foundation_logo.png'), width=300)

st.sidebar.markdown("# Blue Sentinel")
st.sidebar.write(
    """## Why are we here?

Marine ecosystems and global food security are under direct threat from illicit and unsustainable fishing practices, notably bottom trawling. These actions compromise the very foundation of fisheries that numerous communities rely upon for sustenance.

On behalf of the Environmental Justice Foundation, we using advanced satellite tech solutions to precisely pinpoint these harmful fishing activities in real-time, especially within protected marine zones. 

## Objective

Develop a comprehensive monitoring tool to capture precise data on trawling activities and their impacts within marine protected areas (MPAs), given the challenges posed by the vastness and depth of oceans."""

)

st.image('ims/logo.png', width=300)
# latitude = st.number_input('Latitude', value=51.011409)
# longitude = st.number_input('Longitude', value=-1.881302)
mpas = {"Calais": {
    'latitude': 51.011409,
    'longitude': 1.881302,
    'delta_x': 0.65,
    'delta_y': 0.21,
    'polygon': [
    [150, 300],
    [400, 100],
    [800, 200],
    [400, 600],
    [200, 1200],
    [100, 500]
]},
        "Starit of Gibraltar": {
    'latitude': 35.949766,
    'longitude': -5.543646,
    'delta_x': 0.65,
    'delta_y': 0.21,
    'polygon': [
    [300, 350],
    [500, 150],
    [700, 300],
    [550, 550],
    [300, 700],
    [150, 450]
]

        },
        "Le Havre": {
    'latitude': 49.369561,
    'longitude':   -0.197893,
    'delta_x': 0.65,
    'delta_y': 0.21,
    'polygon': [
    [250, 450],
    [230, 850],
    [200, 1200],
    [500, 1200],
    [780, 800],
    [800, 550],
    [680, 450]
]
        }
}
mpa_name = st.selectbox('Select the Marine Protected Area to monitor', list(mpas.keys()))
mpa = mpas[mpa_name]
latitude = mpa['latitude']
longitude = mpa['longitude']
two_weeks_ago = datetime.now() - timedelta(days=14)
default_date = two_weeks_ago
date = st.date_input('Date', value=default_date)
date_end = date + timedelta(days=14)

delta_x = mpa['delta_x']
delta_y = mpa['delta_y']
center = (longitude, latitude)
bbox = (
    center[0] - delta_x / 2,
    center[1] - delta_y / 2,
    center[0] + delta_x / 2,
    center[1] + delta_y / 2,
)
print(bbox)
size = (1400, 932)
time_interval = date.strftime("%Y-%m-%d"), date_end.strftime("%Y-%m-%d")
#time_interval = "2020-07-15", "2020-09-16"
evalscript_true_color = """
//VERSION=3

function setup() {
    return {
        input: [{
            bands: ["VV", "VH"]
        }],
        output: {
            bands: 2
        }
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
"""


config = SHConfig()
if 'sh_client_id' in st.secrets:
    try:
        CLIENT_ID = st.secrets['sh_client_id']
        CLIENT_SECRET = st.secrets['sh_client_secret']
        config.sh_client_id = CLIENT_ID
        config.sh_client_secret = CLIENT_SECRET
    except:
        pass

@st.cache_resource
def get_satelite_image(bbox, size, time_interval):
    bbox = BBox(bbox, crs=CRS.WGS84)
    request = SentinelHubRequest(
        evalscript=evalscript_true_color,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL1,
                time_interval=time_interval
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=bbox,
        size=size,
        config=config,
    )

    image = request.get_data()[0]
    image = image[:, :, 0]
    return image

image = get_satelite_image(bbox, size, time_interval)
# Show in streamlit as simple grayscale image
#st.image(image, clamp=True)
fig, ax = plt.subplots()
ax.imshow(image, cmap="gray")
count_ships = st.checkbox('Count ships')
if 'polygon' in mpa:
    polygon = mpa['polygon']
    polygon = [(y, x) for x, y in polygon]
    closed_polygon = np.array(polygon + [polygon[0]])
    if count_ships:
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, np.int32([polygon]), 1)
        masked_image = image * mask
        sigma = 1
        smoothed_image = filters.gaussian_filter(masked_image.astype(float) / 255, sigma=sigma)
        threshold = 0.3
        thresholded_image = (smoothed_image > threshold).astype(np.uint8)
        labeled_image, num_labels = ndimage.label(thresholded_image)
        for label in range(1, num_labels + 1):
            # Find the center of mass of the connected component.
            y, x = ndimage.measurements.center_of_mass(labeled_image == label)

            # Plot the number of the connected component next to it.
            ax.text(x, y+30, label, color="red", fontsize=11, ha="center", va="center")

        pass
    ax.plot(*zip(*closed_polygon), color="red")
ax.axis('off')



st.pyplot(fig, use_container_width=True)