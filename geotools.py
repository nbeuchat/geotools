from __future__ import division
import math
from motionless import CenterMap
from cStringIO import StringIO
from PIL import Image
import urllib
MERCATOR_RANGE = 256

def bound(value, opt_min, opt_max):
    if (opt_min != None): 
        value = max(value, opt_min)
    if (opt_max != None): 
        value = min(value, opt_max)
    return value

def degreesToRadians(deg) :
    return deg * (math.pi / 180)

def radiansToDegrees(rad) :
    return rad / (math.pi / 180)

class G_Point :
    def __init__(self,x=0, y=0):
        self.x = x
        self.y = y

class G_LatLng :
    def __init__(self,lt, ln):
        self.lat = lt
        self.lng = ln

class MercatorProjection :
    def __init__(self) :
        self.pixelOrigin_ =  G_Point( MERCATOR_RANGE / 2, MERCATOR_RANGE / 2)
        self.pixelsPerLonDegree_ = MERCATOR_RANGE / 360
        self.pixelsPerLonRadian_ = MERCATOR_RANGE / (2 * math.pi)

    def fromLatLngToPoint(self, latLng, opt_point=None) :
        point = opt_point if opt_point is not None else G_Point(0,0)
        origin = self.pixelOrigin_
        point.x = origin.x + latLng.lng * self.pixelsPerLonDegree_
        # NOTE(appleton): Truncating to 0.9999 effectively limits latitude to
        # 89.189.  This is about a third of a tile past the edge of the world tile.
        siny = bound(math.sin(degreesToRadians(latLng.lat)), -0.9999, 0.9999)
        point.y = origin.y + 0.5 * math.log((1 + siny) / (1 - siny)) * -     self.pixelsPerLonRadian_
        return point

    def fromPointToLatLng(self,point) :
        origin = self.pixelOrigin_
        lng = (point.x - origin.x) / self.pixelsPerLonDegree_
        latRadians = (point.y - origin.y) / -self.pixelsPerLonRadian_
        lat = radiansToDegrees(2 * math.atan(math.exp(latRadians)) - math.pi / 2)
        return G_LatLng(lat, lng)

#pixelCoordinate = worldCoordinate * pow(2,zoomLevel)

def getCorners(center, zoom, mapWidth, mapHeight):
    scale = 2**zoom
    proj = MercatorProjection()
    centerPx = proj.fromLatLngToPoint(center)
    SWPoint = G_Point(centerPx.x-(mapWidth/2)/scale, centerPx.y+(mapHeight/2)/scale)
    SWLatLon = proj.fromPointToLatLng(SWPoint)
    NEPoint = G_Point(centerPx.x+(mapWidth/2)/scale, centerPx.y-(mapHeight/2)/scale)
    NELatLon = proj.fromPointToLatLng(NEPoint)
    return {
        'N' : NELatLon.lat,
        'E' : NELatLon.lng,
        'S' : SWLatLon.lat,
        'W' : SWLatLon.lng,
    }
    

def getStaticImageFromBoundingBox(lats,lngs,size=2048,scale=1.0,zoom=12,key=None,maptype='roadmap',return_original=False):
    # Process inputs
    if key is None and size > 640:
        size = 640
    
    ctrlng = (np.max(lngs)+np.min(lngs))/2
    ctrlat = (np.max(lats)+np.min(lats))/2
        
    # Request image from Google and store image
    vmap = CenterMap(lat=ctrlat,lon=ctrlng,zoom=zoom,
                 maptype=maptype,size_x=640,size_y=640,key=key)
    vmap.scale = scale
    url = vmap.generate_url()
    url = url.replace('size=640x640','size={}x{}'.format(size,size))
    print(url)
    
    buffer = StringIO(urllib.urlopen(url).read())
    image = Image.open(buffer)
    
    # Calculate bouding box of image received from Google
    centerPoint = G_LatLng(ctrlat, ctrlng)
    corners = getCorners(centerPoint,zoom,size/scale,size/scale)
    
    # Crop received image to desired bounding box
    wpx = size*abs((np.max(lngs)-np.min(lngs))/(corners['E']-corners['W']))
    hpx = size*abs((np.max(lats)-np.min(lats))/(corners['N']-corners['S']))

    cropx, cropy = wpx / 2.0, hpx / 2.0
    ctrx = ctry = size/2.0
    cimage = image.crop((ctrx-cropx,ctry-cropy,ctrx+cropx,ctry+cropy))
    
    if return_original:
        return cimage,image
    else:
        return cimage
