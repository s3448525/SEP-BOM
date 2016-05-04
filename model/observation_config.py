from model.helpers.distance import GISPoint
from model.schema import RainfallObservation
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
            yield RainfallObservation(
                time=ob_time,
                location=GISPoint(float(obs['mlo']), float(obs['mla'])),
                value=obs['Primary']['drr'],
                source='WOW')
configs.append({
    'name': 'WOW',
    'fetch_func': wow_scraper
})

def bom_scraper():
    url_list = [
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94839.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94838.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94844.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94693.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94831.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94843.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95831.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95832.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95839.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95827.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95835.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94827.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94836.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94841.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94834.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94835.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94826.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94842.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95825.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95822.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94829.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94840.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95845.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94833.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94830.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94828.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95826.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94837.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95840.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94846.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94854.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94852.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95873.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94898.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94864.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94879.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95866.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95872.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94872.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94871.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94857.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94865.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94866.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95936.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94870.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94847.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94886.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94892.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95867.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94863.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94853.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95864.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95874.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95881.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94855.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94861.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95833.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94874.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94859.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94875.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95843.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95836.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94862.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95896.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94884.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94903.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94878.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94888.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94894.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94905.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94906.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95837.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94889.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95853.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94881.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94860.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94882.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94849.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94907.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94949.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94891.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95901.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95913.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.99806.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94900.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94893.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94911.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95890.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94912.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94914.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94933.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94913.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.55039.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95904.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94935.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94930.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94908.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.95918.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.94932.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.99049.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.99051.json",
        "http://www.bom.gov.au/fwo/IDV60801/IDV60801.99052.json"
    ]
    for url in url_list:
        raw_data = urllib.request.urlopen(url)
        data = json.load(raw_data)
        # Create Observation objects
        for obs in data['observations']['data']:
            # Check rain_trace is a valid value, it's not always.
            try:
                value = float(obs['rain_trace'])
            except ValueError:
                value = None
            if value is not None:
                yield RainfallObservation(
                    time = datetime.datetime.strptime(obs['aifstime_utc'], '%Y%m%d%H%M%S'),
                    location = GISPoint(float(obs['lon']), float(obs['lat'])),
                    value = obs['rain_trace'],
                    source = 'BOM')
configs.append({
    'name': 'BOM',
    'fetch_func': bom_scraper
})
