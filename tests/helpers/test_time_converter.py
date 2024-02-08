from datetime import datetime, timedelta
from src.helpers.time_converter import format_time_difference, parse_timestamp
import pytest


def test_parse_timestamp():
    timestamp_str_to_test = "2024-02-08 18:06:37"
    timestamp = parse_timestamp(timestamp_str_to_test)
    assert timestamp == datetime(2024, 2, 8, 18, 6, 37)


def test_parse_timestamp_other_format():
    timestamp_str_to_test = "18.02.2014 18:06:37"
    timestamp = parse_timestamp(timestamp_str_to_test)
    assert timestamp == datetime(2014, 2, 18, 18, 6, 37)


@pytest.mark.parametrize("timestamp_str_to_test, expected_result", [
    ((datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "just now"),
    ((datetime.now() - timedelta(seconds=20)).strftime("%Y-%m-%d %H:%M:%S"), "just now"),
    ((datetime.now() - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"), "1 minute ago"),
    ((datetime.now() - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S"), "2 minutes ago"),
    ((datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"), "1 hour ago"),
    ((datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "2 hours ago"),
    ((datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), "1 day ago"),
    ((datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), "2 days ago"),
    ((datetime.now() - timedelta(weeks=1)).strftime("%Y-%m-%d %H:%M:%S"), "1 week ago"),
    ((datetime.now() - timedelta(weeks=2)).strftime("%Y-%m-%d %H:%M:%S"), "2 weeks ago"),
    ((datetime.now() - timedelta(weeks=5)).strftime("%Y-%m-%d %H:%M:%S"), "1 month ago"),
    ((datetime.now() - timedelta(weeks=9)).strftime("%Y-%m-%d %H:%M:%S"), "2 months ago"),
    ((datetime.now() - timedelta(weeks=53)).strftime("%Y-%m-%d %H:%M:%S"), "1 year ago"),
    ((datetime.now() - timedelta(weeks=105)).strftime("%Y-%m-%d %H:%M:%S"), "2 years ago")])
def test_timedifference_to_string(timestamp_str_to_test, expected_result):
    result = format_time_difference(timestamp_str_to_test)
    assert result == expected_result
