'''
A script to fetch observations and load them into the database.

Usage:
python -m model.load_observation
'''
import model.observation


if __name__ == '__main__':
    # Connect to the db.
    from feva import db
    # Load the observations.
    obs_manager = model.observation.ObservationManager(db)
    obs_count = obs_manager.load()
    print('Observations loaded: '+str(obs_count))

    #import logging
    #logging.basicConfig()
    #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    print(obs_manager.get_observations_near(144.963279, -37.814107, max_distance=50000))
