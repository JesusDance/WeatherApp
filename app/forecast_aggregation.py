from typing import Any

from app.config import settings

START = settings.START
STOP = settings.STOP
END = settings.STEP_EVERY_DAY


def get_min_value(
    value: list, start: int = START, end: int = END, stop: int = STOP
) -> list[Any]:
    average_values = []
    for i in range(start, stop):
        min_value = min(value[start:end], default=None)
        start += 8
        end += 8
        average_values.append(min_value)
    return average_values


def get_max_value(
    value: list, start: int = START, end: int = END, stop: int = STOP
) -> list[Any]:
    average_max_temp = []
    for i in range(start, stop):
        max_value = max(value[start:end], default=None)
        start += 8
        end += 8
        average_max_temp.append(max_value)
    return average_max_temp


def get_average_feels_like_value(
    value: list, start: int = START, end: int = END, stop: int = STOP
) -> list[Any]:
    average_feels_like = []
    for i in range(start, stop):
        average_value = sum(value[start:end]) / 8
        start += 8
        end += 8
        average_feels_like.append(round(average_value, 2))
    return average_feels_like
