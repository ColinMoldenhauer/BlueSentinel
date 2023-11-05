# Blue Sentinel
![Blue Sentinel](ims/logo.png)

This is the code repository for our submission to the [Cassini Hackathon](https://www.cassini.eu/hackathons/), see here for the [full explanation of our project](https://taikai.network/cassinihackathons/hackathons/intdev-humaid/projects/clo4aluu40212uq01n5omhc4c/idea).

## Requirements

This repository is completely written in Python. You can install all dependencies with
`pip : -r requirements.txt`
Some of the code needs credentials from [SentinelHub](https://www.sentinel-hub.com/)

## What is in this repository

There are several parts to this repository. The code in the <aisscrape> folder can be used to collect [AIS data](https://en.wikipedia.org/wiki/Automatic_identification_system), i.e. the data from the automatic tracking system that ships' transceiver are required to transmit. The file [aisscrape.ipynb](aisscrape/aisscrape.ipynb) collects this data by recording data from a commercially and freely available websocket. The file [parse_AISfile.py](aisscrape/parse_AISfile.py) can then be used to parse this data for visualization.

The file [ship_detection.ipynb](dover_ship_detection/ship_detection.ipynb) contains an example of using our algorithm to automatically detect ships in a specified Marine Protected Area (MAP). This is also done with an interactive web front-end using [Streamlit](https://streamlit.io/) in the file <app.py> that is available here: <https://bluesentinel.streamlit.app/>.