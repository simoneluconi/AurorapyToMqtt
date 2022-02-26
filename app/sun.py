from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from suntime import Sun, SunTimeException
import pytz

load_dotenv()

def IsSunUp():
    longitude = float(os.getenv('LONGITUDE'))
    latitude = float(os.getenv('LATITUDE'))

    sun = Sun(latitude, longitude)
    today_sunrise = sun.get_sunrise_time()
    today_sunset = sun.get_sunset_time()

    today_dawn = today_sunrise + timedelta(minutes=-30)
    today_twilight = today_sunset + timedelta (minutes = 30)

    time = datetime.utcnow().replace(tzinfo=pytz.timezone('UTC'))

    return time > today_dawn and time < today_twilight