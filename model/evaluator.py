import datetime
from model.observation import ObservationManager
from model.helpers.web import GeneralException
from model.forecast import ForecastManager
from model.helpers import validator
import logging


class Evaluator(object):

    EVALUATE_SCHEMA = {
        validator.Required('longitude'): validator.Longitude(),
        validator.Required('latitude'): validator.Latitude(),
        validator.Optional('time', default=None): validator.Datetime(),
        validator.Optional('max_distance', default=3000): validator.Coerce(int),
        validator.Optional('weather_type', default='rain'): validator.Coerce(str)
    }
    # The probability of rainfall which gives the 'Umbrella' icon
    RAINFALL_3HR_THRESHOLD = 15
    RAINFALL_24HR_THRESHOLD = 25

    def __init__(self, db):
        self.db = db

    def api_evaluate_lat_lon(self, params):
        params = validator.validate(self.EVALUATE_SCHEMA, params)
        return self.evaluate_lat_lon(**params)

    def evaluate_lat_lon(self, longitude, latitude, time=None, max_distance=3000,  weather_type='rain', obs_source='wow', forecast_source='bom'):
        """
        Find the closest forecasts to the lat/lon at the given time, and
        compare them to the closest observation.
        :param latitude:
        :param longitude:
        :param time:
        :param max_distance: the maximum distance to search
        :param weather_type: currently only supports 'rain'
        :param obs_source: the source for the observation. currently only supports 'wow'
        :param forecast_source: the source of the forecast. currently only supports 'bom'
        :return: the forecast, the observation and the evaluation
        """
        log = logging.getLogger(__name__)

        if time is None:
            time = datetime.datetime.utcnow()

        observation_manager = ObservationManager(self.db)
        forecast_manager = ForecastManager(self.db)
        results = []

        # Find the closest forecasts.
        forecasts = forecast_manager.get_forecasts_near(longitude, latitude,
            time, max_distance=max_distance)
        if len(forecasts) < 1:
            raise GeneralException("No forecast found.")

        # Evaluate each forecast.
        for forecast_value, forecast, fc_dist in forecasts:
            log.debug('Evaluating forecast {} with a value of {}.'.format(
                forecast.name, forecast_value.value))

            # Find the closest observations to the forecast.
            observations = observation_manager.get_observations_near(
                    longitude,
                    latitude,
                    forecast.date_range.lower,
                    forecast.date_range.upper,
                    weather_type,
                    max_distance=max_distance,
                    limit=5000)
            if len(observations) < 1:
                raise GeneralException("No observation found.")
            log.debug('Got {} observations within forecast range.'.format(
                len(observations)))

            # Evaluate the forecast.
            accuracy = self.evaluate(forecast_value, observations)

            # Collect the result.
            results.append(dict(
                forecast=forecast,
                forecast_value=forecast_value,
                observations=observations,
                accuracy=accuracy,
                dist_to_forecast=fc_dist))

        # Return the results.
        return results

    def evaluate(self, forecast_value, observations):
        """
        Function to actually do the comparison
        :param forecast: The forecast object (ORM)
        :param observation: The observation object (ORM)
        :return: True or False
        """
        log = logging.getLogger(__name__)
        # Summarise the observations.
        obs_min = 999999
        obs_max = 0
        obs_avg_sum = 0
        for obs in observations:
            if obs.value < obs_min:
                obs_min = obs.value
            if obs.value > obs_max:
                obs_max = obs.value
            obs_avg_sum += obs.value
        obs_avg = obs_avg_sum / len(observations)

        # Compare forecast and observation values.
        log.debug(('Comparing forecast value {} to observations(min={}, '
            'max={}, avg={}).').format(forecast_value.value, obs_min, obs_max,
                obs_avg))
        if forecast_value.value >= self.RAINFALL_3HR_THRESHOLD and obs_max > 0:
            # predicted rain and was raining
            return True
        elif forecast_value.value < self.RAINFALL_3HR_THRESHOLD and obs_max == 0:
            # didn't predict rain and wasn't raining
            return True
        else:
            return False
