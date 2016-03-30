from flask import Blueprint
from flask.views import MethodView

import model.helpers.web as web
from model.location import LocationManager

api_data_bp = Blueprint('comparisons', 'comparisons', url_prefix='/api')


@api_data_bp.route('/')
@web.api_json_method
def test():
    return "hello world"


class LocationApiHandler(MethodView):

    @web.api_json_method
    def get(self):
        lm = LocationManager(web.get_db())
        return lm.api_locations_near(web.get_parameters())

    @web.api_json_method
    def post(self):
        lm = LocationManager(web.get_db())
        return lm.api_add_location(web.get_post_data())


api_data_bp.add_url_rule('/locations/', view_func=LocationApiHandler.as_view('locations'))
