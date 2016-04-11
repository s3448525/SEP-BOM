import fetch_config
from ftplib import FTP
import gzip
from netCDF4 import Dataset
import datetime


def fetch_forecast(fc_filter={'name': [], 'after': None}):
    '''
    A generator function that fetches the forecast grids specifed by the
    configuration file, optionally filtered by the given filter.

    fc_filter can be used to limit which forecasts are fetched.
    fc_filter['name'] is a list of forecast names, forecasts will only be
        fetched if their name is in the list or the list is empty.
    fc_filter['after'] is optionally a timestamp which specifies only
        forecasts made after this time will be fetched.
    '''
    config = fetch_config.forecast_config
    print(config)
    for detail in config:
        # Call the url generator if one is present.
        if detail['url_generator']:
            detail['urls'] = detail['url_generator']()
        # Fetch forecast(s) via the specified method.
        print(detail)
        if detail['method'] == 'ftp':
            forecasts = fetch_ftp(detail, fc_filter)
        elif detail['method'] == 'opendap':
            forecasts = fetch_opendap(detail, fc_filter)
        else:
            raise Exception('unsupported fetch method')
        # Apply post processing.
        post_process_forecasts(forecasts, detail)
        # Yield each forecast.
        for forecast in forecasts:
            # Yield.
            yield forecast


def fetch_ftp(detail, fc_filter):
    return [] #abort because this functionis not ready for use.
    # Access file via ftp.
    # TODO
    ftp = FTP(details['urls'], details['user'], details['passwd'])
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
    if(detail['gzip']):
        # TODO
        data = gzip.decompress(data)
    # Read data from file.
    # TODO
    # Remove file.
    # TODO
    # Return data.
    # TODO


def fetch_opendap(detail, fc_filter):
    forecasts = []
    for url in detail['urls']:
        # Open dataset via opendap.
        print('Fetching '+url)
        ds = Dataset(url, mode='r')
        # Create a forecast for each time index.
        time_index = 0
        while time_index < len(ds.variables[detail['grid_name']]):
            # Create the forecast based on the config details.
            forecast = detail.copy()
            forecast['url'] = url
            # Copy the relevant data into the forecast.
            forecast['lat_list'] = ds.variables[detail['lat_name']]
            forecast['lon_list'] = ds.variables[detail['lon_name']]
            forecast['values'] = ds.variables[detail['grid_name']][time_index,:,:]
            forecast['created_time'] = detail['created_time_func'](ds, forecast)
            forecast['time'] = detail['forecast_time_func'](
                ds.variables['time'][time_index], forecast['created_time'], ds, detail)
            # Put the netcdf object into the forecast for debugging purpurses.
            #ds.close()
            forecast['netcdf'] = ds
            #
            forecasts.append(forecast)
            break #just for debugging, remove this line
        break #just for debugging, remove this line
    # Return data.
    return forecasts


def post_process_forecasts(forecasts, detail):
    prev_values = None
    for fc in forecasts:
        # Interpret the time value.
#        if detail['time_type'] == 'UnixTime':
#            forecast['time'] = Datetime.fromtimestamp(forecast['time'])
        # Optionally subtract previous values from the current values (usefull
        # for un-accumulating values).
        if detail['sub_prev'] and prev_values:
            forecast['values'] = forecast['time'] - prev_values


def main():
    ''' Display some details of fetched forecasts. '''
    for fc in fetch_forecast():
        print('### Forecast '+fc['name']+' ###')
        print('  Type: '+fc['type'])
        print('  NetCDF Groups:', len(fc['netcdf'].groups))
        print('  NetCDF Dimensions:')
        #print(fc['netcdf'].dimensions)
        for dim in fc['netcdf'].dimensions.values():
            print(dim)
        print('  NetCDF Variables: ', end='')
        #print(fc['netcdf'].variables)
        for var_name in fc['netcdf'].variables:
            print(var_name, end=' ')
        print()
        print('  Grid '+fc['grid_name']+' attributes:')
        for att in fc['netcdf'].variables[fc['grid_name']].ncattrs():
            print(att, fc['netcdf'].variables[fc['grid_name']].getncattr(att), end=' ')
            print()
        print('  Grid '+fc['grid_name']+' dimensions:')
        for dim in fc['netcdf'].variables[fc['grid_name']].dimensions:
            print('    '+dim, end=' ')
        print()
        print('  Grid '+fc['grid_name']+' shape:')
        print(fc['netcdf'].variables[fc['grid_name']].shape)
        print('  Create Time: ', end='')
        print(fc['created_time'])
        print('  Forecast Time: ', end='')
        print(fc['time'])
        print('  Values:')
        print(fc['values'])

if __name__ == '__main__':
    main()
