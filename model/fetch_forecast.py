import model.forecast_config
from ftplib import FTP
import gzip
from netCDF4 import Dataset
import datetime
import sys


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
    configs = model.forecast_config.configs
    print('Number of Forecast Configs: '+str(len(configs)))
    for config in configs:
        # Skip if the name is not in the filter and the filter is active.
        if len(fc_filter['name']) > 0 and (config['name'] not in fc_filter['name']):
            continue
        # Call the url generator if one is present.
        if config['url_generator']:
            config['urls'] = config['url_generator']()
        # Fetch forecast(s) via the specified method.
        if config['method'] == 'ftp':
            forecasts = fetch_ftp(config, fc_filter)
        elif config['method'] == 'opendap':
            forecasts = fetch_opendap(config, fc_filter)
        else:
            raise Exception('unsupported fetch method')
        # Apply post processing.
        post_process_forecasts(forecasts, config)
        # Yield each forecast.
        for forecast in forecasts:
            yield forecast


def fetch_ftp(config, fc_filter):
    for url in config['urls']:
        # Access file via ftp.
        # TODO
        ftp = FTP(url, config['user'], config['passwd'])
        ftp.login()
        tp.cwd('dirpath')
        # Skip file if it has not been modified recently.
        if fc_filter['after']:
            mod_time = string.replace(ftp.sendcmd('MDTM filename'), '213 ', '')
            if datetime.strptime(mod_time, '%Y%m%d%%H%M%S') <= fc_filter['after']:
                return None
        # Download the file.
        # TODO
        ftp.retrbinary('RETR filename', callback)
        ftp.quit()
        # Uncompress file.
        if(config['gzip']):
            # TODO
            data = gzip.decompress(data)
        # Read data from file.
        # TODO
        # Remove file.
        # TODO
        # Return data.
        # TODO


def fetch_opendap(config, fc_filter):
    forecasts = []
    for url in config['urls']:
        # Open dataset via opendap.
        print('Fetching '+url)
        ds = Dataset(url, mode='r')
        # Create a forecast for each time index.
        time_index = 0
        while time_index < len(ds.variables[config['grid_name']]):
            # Create the forecast structure.
            forecast = {
                'name': config['name'],
                'url': url,
                'type': config['type'],
                'lat_list': ds.variables[config['lat_name']][:],
                'lon_list': ds.variables[config['lon_name']][:],
                'values': ds.variables[config['grid_name']][time_index,:,:]
            }
            forecast['creation_time'] = config['creation_time_func'](ds, forecast)
            forecast['time'] = config['forecast_time_func'](
                ds.variables['time'][time_index], forecast, ds, config)
            forecasts.append(forecast)
            time_index += 1
        # Close the opendap dataset.
        ds.close()
        if len(forecasts) == 1: #this is just here for debugging to limit the number of fetched forecasts, TODO remove this later.
            break
    # Return data.
    return forecasts


def post_process_forecasts(forecasts, config):
    prev_values = 0
    for fc in forecasts:
        # Interpret the time value.
#        if config['time_type'] == 'UnixTime':
#            forecast['time'] = Datetime.fromtimestamp(forecast['time'])
        # Optionally subtract previous values from the current values (usefull
        # for un-accumulating values).
        if config['sub_prev']:
            fc['values'] = fc['values'] - prev_values
        # Set prev_values for next time.
        prev_values = fc['values']


def main():
    ''' Display details of fetched forecasts. '''
    # Take CLI arguments as filter names.
    fc_filter = {'name':sys.argv[1:], 'after':None}
    # Fetch and iterate the forecasts.
    for fc in fetch_forecast(fc_filter):
        print('### '+fc['name']+' ###')
        print('  Type: '+fc['type'])
        print('  Creation Time: '+str(fc['creation_time']))
        print('  Forecast Time: '+str(fc['time']))
        print('  Values:')
        print(fc['values'])

if __name__ == '__main__':
    main()
