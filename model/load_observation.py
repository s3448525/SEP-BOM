'''
Fetch observations and load them into the database.

Can be used as a script.
Usage:
python -m model.load_observation
'''
from model.fetch_observation import fetch_observation
from model.schema import RainfallObservation
from sqlalchemy import and_


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

if __name__ == '__main__':
    # Connect to the db.
    from feva import db
    # Load the observations.
    obs_loader = ObservationLoader(db)
    obs_count = obs_loader.load()
    print('Observations loaded: '+str(obs_count))
