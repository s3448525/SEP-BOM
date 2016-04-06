import datetime


#
# Forecast
#
forecast_config = []

# BOM Official Rain Forecast
forecast_config.append({
    'name': 'BOM Official Rain VIC',
    'method': 'ftp',
    'urls': ['ftp://ftp.bom.gov.au/adfd/IDV71097_VIC_WxPrecipitation_SFC.nc.gz'],
    'url_generator':False,
    'type': 'rain',
    'grids': ['WxPrecipitation_SFC'],
    'gzip': True,
    'user': '',
    'passwd': ''
})


# BOM ACCESS VT Rain Forecast
def access_vt_fc_urls():
    """ URL generator for the BOM ACCESS VT Rain Forecast configuration. """
    # Naively presume the url path (alternatively we could have looked up the
    # catalog).
    # Start generating the url.
    base_url = 'http://opendap.bom.gov.au/thredds/dodsC/bmrc/access-vt-fc/ops/surface/'
    time = datetime.datetime.utcnow()
    # Adjust for time difference (forecast appears to be 3 hours behind UTC).
    # TODO: the difference or a timezone may need to go into the config so
    #   that the times can be understood by the application.
    time -= datetime.timedelta(hours=3)
    # Round down to the nearest multiple of 6 hours.
    rounded_hour = time.hour - (time.hour % 6)
    forecast_time = time.strftime('%Y%m%d') + '{:>02}'.format(rounded_hour)
    # Put the date/time components into the url.
    base_url += forecast_time + '/ACCESS-VT_' + forecast_time + '_'
    result = []
    # Generate 36 complete URLs with suffixes from 1 to 36, because the
    # forecast is split across multiple files.
    for x in range(1, 37):
        result.append(base_url + '{:>03}'.format(x) + '_surface.nc')
        #result.append(base_url + '{:>03}'.format(x) + '_surface.nc.dods')
    return result
forecast_config.append({
    'name': 'BOM ACCESS VT Rain',
    'method': 'opendap',
    'urls': [],
    'url_generator': access_vt_fc_urls,
    'type': 'rain',
    'grids': ['accum_prcp']
})

#
# Observation
#
observation_config = []
