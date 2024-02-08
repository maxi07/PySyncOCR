from datetime import datetime, timedelta
import time


def parse_timestamp(timestamp):
    try:
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
    except ValueError:
        pass

    try:
        return datetime.strptime(timestamp, "%d.%m.%Y %H:%M")
    except ValueError:
        pass

    try:
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError("Invalid timestamp format")


def format_time_difference(timestamp):
    updated_time = parse_timestamp(timestamp)
    updated_time_local = convert_string_to_local_timestamp(updated_time)
    now = datetime.now()
    time_difference = now - updated_time_local

    if time_difference < timedelta(seconds=60):
        return "just now"
    elif time_difference < timedelta(minutes=60):
        minutes = time_difference.seconds // 60
        return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
    elif time_difference < timedelta(hours=24):
        hours = time_difference.seconds // 3600
        return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
    elif time_difference < timedelta(days=7):
        days = time_difference.days
        return f"{days} {'day' if days == 1 else 'days'} ago"
    elif time_difference < timedelta(days=30):
        weeks = time_difference.days // 7
        return f"{weeks} {'week' if weeks == 1 else 'weeks'} ago"
    elif time_difference < timedelta(days=365):
        months = time_difference.days // 30
        return f"{months} {'month' if months == 1 else 'months'} ago"
    else:
        years = time_difference.days // 365
        return f"{years} {'year' if years == 1 else 'years'} ago"


# Function to get the local timezone offset and abbreviation
def get_local_timezone_info():
    offset = timedelta(seconds=-time.timezone)
    abbreviation = time.tzname[0] if time.daylight == 0 else time.tzname[1]
    return offset, abbreviation


# Function to convert SQLite timestamp to local timezone# Function to convert string to local timezone timestamp
def convert_string_to_local_timestamp(string_timestamp):
    sqlite_timestamp = datetime.strptime(string_timestamp, "%Y-%m-%d %H:%M:%S")
    offset, _ = get_local_timezone_info()
    local_timestamp = sqlite_timestamp + offset
    return local_timestamp.strftime("%Y-%m-%d %H:%M:%S")
