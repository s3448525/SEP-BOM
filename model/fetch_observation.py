import model.observation_config
import datetime


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
    configs = model.observation_config.configs
    print('Number of Observation Configs: '+str(len(configs)))
    for config in configs:
        for obs in config['fetch_func']():
            yield obs


if __name__ == '__main__':
    print('Observations Sample')
    i = 0
    for obs in fetch_observation():
        print(obs.time, obs.weather_type, obs.value, obs.location.desc)
        i += 1
        if i > 10:
            break
