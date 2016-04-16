from flask import Blueprint

import model.helpers.web as web
from model.location import LocationManager
from model.observation import ObservationManager

api_data_bp = Blueprint('data', 'data', url_prefix='/api')


@api_data_bp.route('/locations/')
@web.api_json_method
def get_locations():
    """
    Hook for return a list of official forecast locations for a given time
    :return:
    """
    lm = LocationManager(web.get_db())
    return lm.api_locations_near(web.get_parameters())


@api_data_bp.route('/locations/observations/')
@web.api_json_method
def get_observation_locations():
    """
    Hook for returning a list of observation points for a given time
    :return:
    """
    observation_manager = ObservationManager(web.get_db())
    return observation_manager.api_get_observations_near(web.get_parameters())


@api_data_bp.route('/evaluate/')
@web.api_json_method
def evaluate_forecast():
    """
    Evaluate a forecast
    :return:
    """
    return dict()
