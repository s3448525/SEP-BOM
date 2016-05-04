'''
Configuration for controlling what and how forecasts are fetched.

The variable 'configs' is a list of configurations. Each configuration in the
list describes a forecast.

Common Configuration Fields
name:
    A short descriptive string that identifies the forecast.
method:
    Method for fetching the forecast. Supported methods: 'opendap' and 'ftp'.
urls:
    A list of zero or more URLs that defines where the forecast(s) are
    fetched from.
url_generator:
    Optionally a function that outputs a list of URLs. The returned list
    will replace the config 'urls'. Set to None to disable.
type:
    The type of forecast, eg 'rain'.
grid_name:
    The NetCDF dataset variable name that holds the forecast values,
    eg 'precipitation'.
lat_name:
    The NetCDF dataset dimension name that holds the latitude values,
    eg 'lat'.
lon_name:
    The NetCDF dataset dimension name that holds the longitude values,
    eg 'lon'.
lat_step:
    The step size along the latitude dimension used when copying forecast
    values. A data reduction feature to aid performance at the cost of spatial
    resolution. Eg a step size of 1 copies every element along the latitude
    dimension (no reduction), a step size of 2 copies every other, a step
    size of 3 copies every third, etc.
lon_step:
    The step size along the longitude dimension used when copying forecast
    values. A data reduction feature to aid performance at the cost of spatial
    resolution. Eg a step size of 1 copies every element along the longitude
    dimension (no reduction), a step size of 2 copies every other, a step
    size of 3 copies every third, etc.
forecast_time_func:
    Optionally a function that returns a datetime object that specifies the
    time the forecast applies. Set to None to disable.
creation_time_func:
    Optionally a function that returns a datetime object that specifies the
    time the forecast was created. Set to None to disable.
sub_prev:
    When set to True; forecast values will be substracted by the previously
    fetched forecast values. Can be used to un-accumulate a series of
    forecasts. Set to False to disable.
'''
import datetime


configs = []

# BOM Official Rain Forecast IDV71097
def adfd_creation_time(dataset, forecast):
    return datetime.datetime.utcfromtimestamp(dataset.getncattr('creationTime'))
def adfd_forecast_time(raw_time, forecast, dataset, config):
    start_time = datetime.datetime.utcfromtimestamp(raw_time)
    end_time = start_time + datetime.timedelta(hours=3)
    return (start_time, end_time)
configs.append({
    'name': 'BOM Official Rain VIC',
    'method': 'ftp',
    'urls': ['ftp://ftp.bom.gov.au/adfd/IDV71013_VIC_PoP_SFC.nc.gz'],
    'url_generator': None,
    'type': 'prob_prcp',
    'grid_name': 'PoP_SFC',
    'lat_name': 'latitude',
    'lon_name': 'longitude',
    'lat_step': 2,
    'lon_step': 2,
    'forecast_time_func': adfd_forecast_time,
    'creation_time_func': adfd_creation_time,
    'sub_prev': False,
    'gzip': True,
    'user': 'bom054',
    'passwd': 'leadEr6g'
})


# BOM ACCESS VT Rain Forecast
#def access_vt_fc_urls():
#    ''' URL generator for the BOM ACCESS VT Rain Forecast configuration. '''
#    # Naively presume the url path (alternatively we could have looked up the
#    # catalog).
#    # Start generating the url.
#    base_url = 'http://opendap.bom.gov.au/thredds/dodsC/bmrc/access-vt-fc/ops/surface/'
#    time = datetime.datetime.utcnow()
#    # Adjust for time difference (forecast appears to be 3 hours behind UTC).
#    # TODO: the difference or a timezone may need to go into the config so
#    #   that the times can be understood by the application.
#    time -= datetime.timedelta(hours=3)
#    # Round down to the nearest multiple of 6 hours.
#    rounded_hour = time.hour - (time.hour % 6)
#    forecast_time = time.strftime('%Y%m%d') + '{:>02}'.format(rounded_hour)
#    # Put the date/time components into the url.
#    base_url += forecast_time + '/ACCESS-VT_' + forecast_time + '_'
#    result = []
#    # Generate 37 complete URLs with suffixes from 0 to 36, because the
#    # forecast is split across multiple files.
#    for x in range(0, 37):
#        result.append(base_url + '{:>03}'.format(x) + '_surface.nc')
#        #result.append(base_url + '{:>03}'.format(x) + '_surface.nc.dods')
#    return result
#def access_vt_fc_creation_time(dataset, forecast):
#    ''' Get the time the forecast was created, for the BOM ACCESS VT Rain Forecast configuration. '''
#    string_offset = len('http://opendap.bom.gov.au/thredds/dodsC/bmrc/access-vt-fc/ops/surface/')
#    time_string = forecast['url'][string_offset:string_offset+10]
#    creation_time = datetime.datetime(
#        year=int(time_string[:4]),
#        month=int(time_string[4:6]),
#        day=int(time_string[6:8]),
#        hour=int(time_string[8:10]))
#    # Convert to UTC timezone.
#    creation_time += datetime.timedelta(hours=3) #TODO check the adjustment amount is correct.
#    return creation_time
#def access_vt_fc_forecast_time(raw_time, forecast, dataset, config):
#    ''' Get the time the forecast applies, for the BOM ACCESS VT Rain Forecast configuration. '''
#    start_time = forecast['creation_time'] + datetime.timedelta(days=raw_time)
#    end_time = start_time + datetime.timedelta(hours=1)
#    return (start_time, end_time)
#configs.append({
#    'name': 'BOM ACCESS VT Rain',
#    'method': 'opendap',
#    'urls': [],
#    'url_generator': access_vt_fc_urls,
#    'type': 'accum_prcp',
#    'grid_name': 'accum_prcp',
#    'lat_name': 'lat',
#    'lon_name': 'lon',
#    'lat_step': 2,
#    'lon_step': 2,
#    'forecast_time_func': access_vt_fc_forecast_time,
#    'creation_time_func': access_vt_fc_creation_time,
#    'sub_prev': True
#})
