import os
import json
import pytz
from datetime import datetime

filepath: str = os.path.join("alarm", "alarm.json")


def save_data(alarm_time: datetime, time_zone: pytz.tzinfo.DstTzInfo) -> None:
    """Save alarm time and time zone to a JSON file."""
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)
    else:
        data = {}

    if alarm_time:
        data['alarm'] = alarm_time.isoformat()
    if time_zone:
        data['time_zone'] = time_zone.zone

    with open(filepath, 'w') as file:
        json.dump(data, file)


def load_data() -> dict:
    """Load alarm time and time zone from a JSON file."""
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)
            if 'alarm' in data:
                data['alarm'] = datetime.fromisoformat(data['alarm'])
            if 'time_zone' in data:
                data['time_zone'] = pytz.timezone(data['time_zone'])
            return data
    return {}
