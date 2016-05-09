from model.helpers.distance import GISPoint, Distance, Within, AsLatLon, decode_point
from model.fetch_observation import fetch_observation
from model.schema import RainfallObservation
from psycopg2.extras import DateTimeRange
import datetime

class ObservationManager(object):

    def __init__(self, db):
        self.db = db

    def api_get_observations_near(self, params):
        return self.get_observations_near(None, None)

    def get_observations_near(self, longitude, latitude, start_time=None, end_time=None, weather_type='rain', max_distance=1000, limit=10):
        """
        :param longitude:
        :param latitude:
        :param start_time:
        :param end_time:
        :param distance: The distance (in meters) of the bounds
        :param limit: How many records to return (sorted by distance)
        :return: A list of observations near a given coordinate.
        """
        # If no start time is specified use the current time.
        if start_time is None:
            start_time = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
            end_time = start_time + datetime.timedelta(hours=4)
        # Query the DB for observations.
        point = GISPoint(longitude, latitude)
        observations = self.db.session.query(RainfallObservation)\
            .filter(Within(RainfallObservation.location, point, max_distance))\
            .filter(RainfallObservation.time > start_time)\
            .filter(RainfallObservation.time <= end_time)\
            .order_by(Distance(RainfallObservation.location, point))\
            .limit(limit)\
            .all()
        return observations

    def add_observation(self, latitude, longitude, time, value, source):
        pass

    def load(self):
        '''
        Fetch observations and load them into the DB.
        '''
        # Fetch each observation.
        obs_count = 0
        with self.db.transaction_session() as session:
            for obs in fetch_observation():
                # Skip adding if object already exists.
                if session.query(RainfallObservation.time)\
                        .filter(RainfallObservation.time == obs.time)\
                        .filter(RainfallObservation.location == obs.location)\
                        .one_or_none() is not None:
                    continue
                session.add(obs)
                obs_count += 1
                # Commit to the DB in batches for improved speed.
                if obs_count % 1000 == 0:
                    session.commit()
            # Commit remaining uncommitted observations.
            session.commit()
        return obs_count
