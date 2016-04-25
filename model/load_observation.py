'''
Fetch observations and load them into the database.

Can be used as a script.
Usage:
python -m model.load_observation
'''
from model.helpers.distance import GISPoint, Distance, Within, AsLatLon, decode_point
from model.fetch_observation import fetch_observation
from model.schema import RainfallObservation
from psycopg2.extras import DateTimeRange
import datetime


class ObservationLoader(object):

    def __init__(self, db):
        self.db = db

    def load(self):
        '''
        Fetch observations and load them into the DB.
        '''
        # Fetch each observation.
        obs_count = 0
        with self.db.session_scope() as session:
            for obs in fetch_observation():
                # Skip adding if object already exists.
                if session.query(RainfallObservation.time).filter(RainfallObservation.time == obs.time).filter(RainfallObservation.location == obs.location).one_or_none() is not None:
                    continue
                session.add(obs)
                obs_count += 1
                # Commit to the DB in batches.
                if obs_count % 1000 == 0:
                    session.commit()
            # Commit remaining uncommitted observations.
            session.commit()
        return obs_count

    def observations_near(self, longitude, latitude, start_time=None, end_time=None, distance=1000, limit=5):
        """
        :param longitude:
        :param latitude:
        :param time:
        :param distance: The distance (in meters) of the bounds
        :param limit: How many records to return (sorted by distance)
        :return: A list of locations (as a dict) near a given coordinate.
        """
        if start_time is None:
            start_time = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
            end_time = start_time + datetime.timedelta(hours=4)

        point = GISPoint(longitude, latitude)
        observations = []
        with self.db.session_scope() as session:
            observations = session.query(RainfallObservation)\
                .filter(Within(RainfallObservation.location, point, distance))\
                .filter(RainfallObservation.time > start_time)\
                .filter(RainfallObservation.time <= end_time)\
                .order_by(Distance(RainfallObservation.location, point)).limit(limit)\
                .all()
        return observations

if __name__ == '__main__':
    # Connect to the db.
    from feva import db
    # Load the observations.
    obs_loader = ObservationLoader(db)
    obs_count = obs_loader.load()
    print('Observations loaded: '+str(obs_count))

    #import logging
    #logging.basicConfig()
    #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    print(obs_loader.observations_near(144.963279, -37.814107, distance=50000))
