import model.forecast_config
from urllib.parse import urlparse
from ftplib import FTP
import gzip
from netCDF4 import Dataset
import datetime
import sys
import os
from io import BytesIO
import tempfile
import logging

def fetch_forecast(fc_filter={'name': [], 'after': None}):
    '''
    A generator function that fetches forecasts specifed by the configuration
    file, optionally filtered by the given filter.

    fc_filter can be used to limit which forecasts are fetched.
    fc_filter['name'] is a list of forecast names, forecasts will only be
        fetched if their name is in the list or the list is empty.
    fc_filter['after'] is optionally a timestamp which specifies only
        forecasts made after this time will be fetched.
    '''
    log = logging.getLogger(__name__)
    configs = model.forecast_config.configs
    log.debug('Number of Forecast Configs: '+str(len(configs)))
    for config in configs:
        # Skip if the name is not in the filter and the filter is active.
        if len(fc_filter['name']) > 0 and (config['name'] not in fc_filter['name']):
            continue
        # Call the url generator if one is present.
        if config['url_generator'] is not None:
            config['urls'] = config['url_generator']()
        # Fetch forecast(s) via the specified method.
        if config['method'] == 'ftp':
            forecasts = fetch_ftp(config, fc_filter)
        elif config['method'] == 'opendap':
            forecasts = fetch_opendap(config, fc_filter)
        else:
            raise Exception('unsupported fetch method')
        # Skip forecast if it was not created recently.
        # TODO
        # Apply post processing.
        post_process_forecasts(forecasts, config)
        # Yield each forecast.
        for forecast in forecasts:
            yield forecast


def fetch_ftp(config, fc_filter):
    log = logging.getLogger(__name__)
    forecasts = []
    for url in config['urls']:
        # Access file via ftp.
        url_parts = urlparse(url)
        data_dir = os.path.dirname(url_parts.path)[1:]
        data_name = os.path.basename(url_parts.path)
        log.debug('Fetching {} ({} {})'.format(url, data_dir, data_name))
        ftp = FTP(url_parts.hostname, config['user'], config['passwd'])
#TODO detect and handle failed connection
        ftp.login(user=config['user'], passwd=config['passwd'])
#TODO detect and handle failed login
        ftp.cwd(data_dir)
#        # Skip file if it has not been modified recently.
#        if fc_filter['after']:
#            mod_time = string.replace(ftp.sendcmd('MDTM filename'), '213 ', '')
#            log.debug('mod_time: {}'.format(str(mod_time)))
#            if datetime.strptime(mod_time, '%Y%m%d%%H%M%S') <= fc_filter['after']:
#                return None
        # Download the file.
        raw_data = BytesIO()
        ftp.retrbinary('RETR '+data_name, raw_data.write)
        ftp.quit()
        temp_file = tempfile.NamedTemporaryFile(mode='w+b', prefix='feva_', delete=False)
        temp_file_name = temp_file.name
        # Write to a temp file.
        if(config['gzip']):
            # Decompress and write to file.
            log.debug('Un-gzipping & writing to temp file ({}).'.format(temp_file_name))
            temp_file.write(gzip.decompress(raw_data.getvalue()))
        else:
            # Otherwise just write to file.
            log.debug('Writing to temp file ({}).'.format(temp_file_name))
            temp_file.write(raw_data.getvalue())
        raw_data.close()
        temp_file.close()
        # Open the dataset.
        log.debug('Opening temp file dataset.')
        ds = Dataset(temp_file_name, mode='r')
        # Create a forecast for each time index.
        time_index = 0
        while time_index < len(ds.variables[config['grid_name']]):
            # Create the forecast structure.
            forecast = {
                'name': config['name'],
                'url': url,
                'type': config['type'],
                'lat_list': ds.variables[config['lat_name']][::config['lat_step']],
                'lon_list': ds.variables[config['lon_name']][::config['lon_step']],
                'values': ds.variables[config['grid_name']][time_index, ::config['lat_step'], ::config['lon_step']]
            }
            forecast['creation_time'] = config['creation_time_func'](ds, forecast)
            forecast['start_time'], forecast['end_time'] = config['forecast_time_func'](
                ds.variables['time'][time_index], forecast, ds, config)
            forecasts.append(forecast)
            time_index += 1
        # Close the dataset.
        ds.close()
        # Remove the temp file.
        log.debug('Deleteing temp file: {}'.format(temp_file_name))
        os.remove(temp_file_name)
    # Return data.
    return forecasts


def fetch_opendap(config, fc_filter):
    log = logging.getLogger(__name__)
    forecasts = []
    for url in config['urls']:
        # Open dataset via opendap.
        log.debug('Fetching '+url)
        ds = Dataset(url, mode='r')
        # Create a forecast for each time index.
        time_index = 0
        while time_index < len(ds.variables[config['grid_name']]):
            # Create the forecast structure.
            forecast = {
                'name': config['name'],
                'url': url,
                'type': config['type'],
                'lat_list': ds.variables[config['lat_name']][::config['lat_step']],
                'lon_list': ds.variables[config['lon_name']][::config['lon_step']],
                'values': ds.variables[config['grid_name']][time_index, ::config['lat_step'], ::config['lon_step']]
            }
            forecast['creation_time'] = config['creation_time_func'](ds, forecast)
            forecast['start_time'], forecast['end_time'] = config['forecast_time_func'](
                ds.variables['time'][time_index], forecast, ds, config)
            forecasts.append(forecast)
            time_index += 1
        # Close the opendap dataset.
        ds.close()
    # Return data.
    return forecasts


def post_process_forecasts(forecasts, config):
    prev_values = 0
    for fc in forecasts:
        # Optionally subtract previous values from the current values (useful
        # for un-accumulating values).
        if config['sub_prev']:
            fc['values'] = fc['values'] - prev_values
        # Set prev_values for next time.
        prev_values = fc['values']


def main():
    ''' Display details of fetched forecasts. '''
    # Take CLI arguments as filter names.
    fc_filter = {'name': sys.argv[1:], 'after': None}
    # Fetch and iterate the forecasts.
    for fc in fetch_forecast(fc_filter):
        print('### '+fc['name']+' ###')
        print('  Type: '+fc['type'])
        print('  Creation Time: '+str(fc['creation_time']))
        print('  Forecast Time: {} - {}'.format(str(fc['start_time']), str(fc['end_time'])))
        print('  Grid Size: {}, {}'.format(len(fc['lat_list']), len(fc['lon_list'])))
        print('  Latitudes Sample:')
        print(fc['lat_list'][:5])
        print('  Longitudes Sample:')
        print(fc['lon_list'][:5])
        print('  Values:')
        print(fc['values'])

if __name__ == '__main__':
    main()
