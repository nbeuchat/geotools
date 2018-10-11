# Geotools
Simple utility functions to get a static image from the Google Maps API. This function returns a static image of the map that contains every points passed as input. 

## Usage

```
from geotools import getStaticImageFromBoundingBox
lats = [46.520134, 46.509465, 46.525679]
lngs = [6.565685, 6.633829, 6.642597]
gmap_api_key = '<YOUR GOOGLE MAPS API KEY HERE>'
map_image = getStaticImageFromBoundingBox(lats,lngs,size=2048,scale=1.0,zoom=12,key=gmap_api_key,maptype='roadmap',return_original=False)
map_image.show()
```
