from model.helpers.distance import GISPoint
from model.schema import Observation
import urllib.request
import urllib.parse
import datetime
from flask import json


configs = []

# WOW unofficial observations
def wow_scraper():
    '''
    Unofficial WOW observation scraper.
    A generator function that yields Observation objects.
    '''
    # Get JSON dump.
    ob_time = datetime.datetime.utcnow()
    ob_time = ob_time.replace(minute=0, second=0, microsecond=0)
    url_params = urllib.parse.urlencode({
        'timePointSlider': '0',
        'timePointPicker': '-1',
        'northLat': '-37.66152049063651',
        'southLat': '-37.96637879553983',
        'eastLon': '145.18781308105463',
        'westLon': '144.73874691894525',
        'centerLat': '-37.814107',
        'centerLon': '144.96327999999994',
        'zoom': '12',
        'mapTime': ob_time.strftime('%d/%m/%Y %H:59'),
        'useSlider': 'false',
        'mapLayer': 'rainfall_rate',
        'showWowData': 'on',
        'mapFilterTags': ''
    })
    url = '{}?{}'.format(
        'http://wow.metoffice.gov.uk/ajax/home/map',
        url_params)
    raw_data = urllib.request.urlopen(url)
    data = json.load(raw_data)
    # Create Observation objects
    for obs in data['r']:
        if 'drr' in obs['Primary']:
            yield Observation(
                time=ob_time,
                location=GISPoint(float(obs['mlo']), float(obs['mla'])),
                weather_type='rain',
                value=obs['Primary']['drr'],
                source='WOW')
configs.append({
    'name': 'WOW',
    'fetch_func': wow_scraper
})
