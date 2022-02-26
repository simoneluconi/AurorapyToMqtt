from datetime import datetime, timedelta
from suntime import Sun, SunTimeException
import pytz

def IsSunUp():
    longitude = 6.404010057449341
    latitude = 46.644479344712764

    sun = Sun(latitude, longitude)
    today_sunrise = sun.get_sunrise_time()
    today_sunset = sun.get_sunset_time()

    today_dawn = today_sunrise + timedelta(minutes=-30)
    today_twilight = today_sunset + timedelta (minutes = 30)

    time = datetime.utcnow().replace(tzinfo=pytz.timezone('UTC'))

    return time > today_dawn and time < today_twilight