import datetime
from model.observation import ObservationManager
from model.helpers.web import GeneralException
from model.load_forecast import ForecastLoader


class Evaluator(object):

    # The probability of rainfall which gives the 'Umbrella' icon
    RAINFALL_THRESHOLD = 20

    def __init__(self, db):
        self.db = db

    def evaluate_lat_lon(self, longitude, latitude, time=datetime.datetime.utcnow(), max_distance=1000,  weather_type='rain', obs_source='wow', forecast_source='BOM'):
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
        observation_manager = ObservationManager(self.db)
        forecast_manager = ForecastLoader(self.db)

        # find the closest observation
        observation = observation_manager.get_observations_near(longitude, latitude, time, weather_type, max_distance=max_distance, limit=1)
        if observation is None:
            raise GeneralException("No observation found.")

        # find the closest forecast
        # TODO: modify the below call to return a forecast object rather than a dict
        forecast = forecast_manager.forecasts_near(longitude, latitude, time, distance=max_distance, limit=1)
        if not forecast:
            raise GeneralException("No forecast found.")

        # return the result
        return dict(forecast=forecast, observation=observation, evaluation=self.evaluate(forecast, observation))

    def evaluate(self, forecast, observation):
        """
        Function to actually do the comparison
        :param forecast: The forecast object (ORM)
        :param observation: The observation object (ORM)
        :return: True or False
        """
        if forecast.value >= self.RAINFALL_THRESHOLD and observation.value > 0:
            # predicted rain and was raining
            return True

        elif forecast.value < self.RAINFALL_THRESHOLD and observation == 0:
            # didn't predict rain and wasn't raining
            return True
        else:
            return False
