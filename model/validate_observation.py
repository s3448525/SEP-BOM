import model.schema
import logging

# Rainfall limits in millilitres per hour.
# Max leniently based on http://www.bom.gov.au/water/designRainfalls/rainfallEvents/worldRecRainfall.shtml
RAINFALL_1HR_MAX = 405.0
RAINFALL_1HR_MIN = 0.0

# Temperature limits in celsius.
TEMPERATURE_MAX = 55.0
TEMPERATURE_MIN = -55.0


def is_rainfall_valid(observation):
    return (float(observation.value) <= RAINFALL_1HR_MAX) and \
        (float(observation.value) >= RAINFALL_1HR_MIN)


def is_temperature_valid(observation):
    return (observation.value <= TEMPERATURE_MAX) and \
        (observation.value >= TEMPERATURE_MIN)
