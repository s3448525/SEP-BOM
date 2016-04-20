'''
Fetch observations and load them into the database.

Can be used as a script.
Usage:
python -m model.load_observation db_host db_port db_user db_password
Example:
python -m model.load_observation 127.0.0.1 5432 myname mypassword
'''
from model.fetch_observation import fetch_observation
#from model.schema import Observation


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
                session.add(obs)
                obs_count += 1
                # Commit to the DB in batches.
                if obs_count % 1000 == 0:
                    session.commit()
            # Commit remaining uncommitted observations.
            session.commit()
        return obs_count

if __name__ == '__main__':
    import sys
    from model.orm import ORM
    # Print usage if needed.
    if len(sys.argv) != 5:
        sys.exit('Usage: python -m model.load_observation host port username password')
    # Connect to the db.
    db = ORM(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
    # Load the observations.
    obs_loader = ObservationLoader(db)
    obs_count = obs_loader.load()
    print('Observations loaded: '+str(obs_count))
