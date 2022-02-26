import ephem
from datetime import datetime

def IsSunUp():
    sun = ephem.Sun()
    mlv = ephem.Observer()
    mlv.lon = 6.404010057449341
    mlv.lat = 46.644479344712764
    mlv.elevation = 864
    mlv.date = datetime.now()
    sun.compute(mlv)
    twilight = -12 * ephem.degree
    return sun.alt > twilight