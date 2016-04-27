import datetime
from model.observation import ObservationManager
from model.helpers.web import GeneralException
from model.forecast import ForecastManager
from model.helpers import validator


class Evaluator(object):

    EVALUATE_SCHEMA = {
        validator.Required('longitude'): validator.Longitude(),
        validator.Required('latitude'): validator.Latitude(),
        validator.Optional('time', default=None): validator.Datetime(),
        validator.Optional('max_distance', default=3000): validator.Coerce(int),
        validator.Optional('weather_type', default='rain'): validator.Coerce(str)
    }
    # The probability of rainfall which gives the 'Umbrella' icon
    RAINFALL_THRESHOLD = 20

    def __init__(self, db):
        self.db = db

    def api_evaluate_lat_lon(self, params):
        params = validator.validate(self.EVALUATE_SCHEMA, params)
        return self.evaluate_lat_lon(**params)

    def evaluate_lat_lon(self, longitude, latitude, time=None, max_distance=3000,  weather_type='rain', obs_source='wow', forecast_source='BOM'):
        """
        Find the closest station to the lat/lon at the given time, and compare it to the closest observation
        :param latitude:
        :param longitude:
        :param time:
        :param max_distance: the maximum distance to search
        :param weather_type: currently only supports 'rain'
        :param obs_source: the source for the observation. currently only supports 'wow'
        :param forecast_source: the source of the forecast. currently only supports 'bom'
        :return: the forecast, the observation and the evaluation
        """

        if time is None:
            time = datetime.datetime.utcnow()

        observation_manager = ObservationManager(self.db)
        forecast_manager = ForecastManager(self.db)

        # find the closest forecast
        # TODO: modify the below call to return a forecast object rather than a dict
        forecast_value, forecast = forecast_manager.get_forecasts_near(longitude, latitude, time, max_distance=max_distance, limit=1)[0]
        if not forecast:
            raise GeneralException("No forecast found.")
        print(forecast_value, forecast)
        # find the closest observation
        observation = observation_manager.get_observations_near(longitude, latitude, forecast.date_range.lower, forecast.date_range.upper, weather_type, max_distance=max_distance, limit=1)
        if observation is None:
            raise GeneralException("No observation found.")

        # return the result
        return dict(forecast=forecast, observation=observation, evaluation=self.evaluate(forecast_value, observation))

    def evaluate(self, forecast_value, observation):
        """
        Function to actually do the comparison
        :param forecast: The forecast object (ORM)
        :param observation: The observation object (ORM)
        :return: True or False
        """
        if forecast_value.value >= self.RAINFALL_THRESHOLD and observation.value > 0:
            # predicted rain and was raining
            return True

        elif forecast_value.value < self.RAINFALL_THRESHOLD and observation == 0:
            # didn't predict rain and wasn't raining
            return True
        else:
            return False
