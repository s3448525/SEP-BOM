from model.helpers.distance import GISPoint, Distance, Within, AsLatLon, decode_point
from model.helpers import validator
from model.fetch_observation import fetch_observation
from model.schema import RainfallObservation
from psycopg2.extras import DateTimeRange
import datetime
import logging


class ObservationManager(object):

    EVALUATE_SCHEMA = {
        validator.Required('longitude'): validator.Longitude(),
        validator.Required('latitude'): validator.Latitude(),
        validator.Optional('start_time', default=None): validator.Datetime(),
        validator.Optional('end_time', default=None): validator.Datetime(),
        validator.Optional('weather_type', default='rain'): validator.Coerce(str),
        validator.Optional('max_distance', default=1000): validator.Coerce(int),
        validator.Optional('limit', default=10): validator.Coerce(int)
    }

    def __init__(self, db):
        self.db = db

    def api_get_observations_near(self, params):
        params = validator.validate(self.EVALUATE_SCHEMA, params)
        return self.get_observations_near(**params)

    def get_observations_near(self, longitude, latitude, start_time=None, end_time=None, weather_type='rain', source='', max_distance=1000, limit=10):
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
        optional_filters = {}
        if source:
            optional_filters['source'] = source
        observations = self.db.session.query(RainfallObservation)\
            .filter(Within(RainfallObservation.location, point, max_distance))\
            .filter(RainfallObservation.time > start_time)\
            .filter(RainfallObservation.time <= end_time)\
            .filter_by(**optional_filters)\
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

    def delete_old(self, time):
        '''
        Delete observations older than the specified datetime.
        Returns the number of deleted observations.
        '''
        log = logging.getLogger(__name__)
        with self.db.transaction_session() as session:
            deleted_count = session.query(RainfallObservation)\
                .filter(RainfallObservation.time < time)\
                .delete()
            session.commit()
        log.debug('Deleted {} observations older than {}.'.format(str(deleted_count), str(time)))
        return deleted_count
