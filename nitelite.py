#!env python3

from datetime import datetime, date
import requests
import subprocess

import pytz

ratios = {
    'astronomical_twilight_begin': 0,
    'nautical_twilight_begin': 0.25,
    'civil_twilight_begin': 0.5,
    'sunrise': 1,
    'solar_noon': 1,
    'sunset': 1,
    'civil_twilight_end': 0.5,
    'nautical_twilight_end': 0.20,
    'astronomical_twilight_end': 0,
    'midnight': 0,
}

ip_info = requests.get("https://ipinfo.io").json()
lat, lon = ip_info["loc"].split(",")

sunset_info = requests.get(f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0").json()

day_brightness = 0.85
night_brightness = 0.5

day_temp = 6400
night_temp = 3200

now = pytz.utc.localize(datetime.utcnow())
event_dates = {k: datetime.fromisoformat(v) for k, v in sunset_info["results"].items() if k != "day_length"}
event_dates["midnight"] = pytz.utc.localize(datetime.combine(date.today(), datetime.max.time()))

before = None
after = None

for event in sorted(event_dates, key=lambda k: event_dates[k]):
    if now > event_dates[event]:
        before = event
    if now < event_dates[event]:
        after = event
        break

before_ratio = ratios[before]
after_ratio = ratios[after] if after is not None else 0

before_to_now = now - event_dates[before]
before_to_after = event_dates[after] - event_dates[before]

print(f"before: {before} - {before_ratio} - {before_to_now}")
print(f"after: {after} - {after_ratio} - {before_to_after}")

alpha = before_to_now / before_to_after
print(alpha)

ratio = alpha * after_ratio + (1 - alpha) * before_ratio
print(ratio)

brightness = ratio * day_brightness + (1.0 - ratio) * night_brightness
temp = ratio * day_temp + (1.0 - ratio) * night_temp

print(f"{int(temp)} {brightness}")
subprocess.call(["/usr/local/bin/sct", str(int(temp)), str(brightness)])
print("Done")
