import model.observation_config
import model.validate_observation
import datetime
import logging
import sys


def fetch_observation(obs_filter={'name': [], 'after': None}):
    '''
    A generator function that fetches observations specifed by the
    configuration file, optionally filtered by the given filter.

    obs_filter can be used to limit which observations are fetched.
    obs_filter['name'] is a list of observation providers, observations will
        only be fetched from providers whose name is in the list or if the
        list is empty.
    fc_filter['after'] is optionally a timestamp which specifies only
        observations made after this time will be fetched.
    '''
    log = logging.getLogger(__name__)
    configs = model.observation_config.configs
    log.debug('Number of Observation Configs: '+str(len(configs)))
    for config in configs:
        for obs in config['fetch_func']():
            if model.validate_observation.is_rainfall_valid(obs):
                yield obs
            else:
                log.debug('Invalid rainfall value: {}'.format(obs.value))


if __name__ == '__main__':
    # Optionally output debug messages.
    if 'debug' in sys.argv:
        log_handler = logging.StreamHandler(sys.stderr)
        log_handler.setLevel(logging.DEBUG)
        log_fmt = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(log_fmt)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger().addHandler(log_handler)

    print('Observations Sample')
    i = 0
    for obs in fetch_observation():
        print(obs.time, obs.value, obs.location.desc, obs.source)
        i += 1
        if i > 10:
            break
