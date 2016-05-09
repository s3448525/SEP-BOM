'''
A script to fetch observations and load them into the database.

Usage:
python -m model.load_observation [debug]
'''
import model.observation
import logging
import sys


if __name__ == '__main__':
    # Connect to the db.
    from feva import db

    # Optionally output debug messages.
    if 'debug' in sys.argv:
        log_handler = logging.StreamHandler(sys.stderr)
        log_handler.setLevel(logging.DEBUG)
        log_fmt = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(log_fmt)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger().addHandler(log_handler)

    # Load the observations.
    obs_manager = model.observation.ObservationManager(db)
    obs_count = obs_manager.load()
    logging.getLogger(__name__).debug('Observations loaded: '+str(obs_count))
