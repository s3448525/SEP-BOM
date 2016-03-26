from model.schema import Location
from core.distance_helpers import GISPoint, Within, Distance
from core import validator


class LocationManager(object):

    ADD_LOCATION_SCHEMA = {
        validator.Required('Name'): str,
        validator.Required('Latitude'): validator.Coerce(float),
        validator.Required('Longitude'): validator.Coerce(float)
    }

    LOCATIONS_NEAR_SCHEMA = {
        validator.Required('Latitude'): validator.Coerce(float),
        validator.Required('Longitude'): validator.Coerce(float),
        validator.Optional('Distance', default=1000): validator.Coerce(float),
        validator.Optional('Limit', default=5): validator.Coerce(int)
    }

    def __init__(self, db):
        self.db = db

    def api_add_location(self, params):
        params = validator.validate(self.ADD_LOCATION_SCHEMA, params)
        self.add_location(params['Name'], params['Longitude'], params['Latitude'])
        return "Location Added."

    def add_location(self, name, longitude, latitude):
        """
        Adds a location to the database
        :param name: The name of the location
        :param longitude: longitudinal coordinate
        :param latitude: latitudinal coordinate
        :return:
        """
        location = Location(name=name, geom=GISPoint(longitude, latitude))

        with self.db.session_scope() as session:
            session.add(location)

    def api_locations_near(self, params):
        params = validator.validate(self.LOCATIONS_NEAR_SCHEMA, params)
        return self.locations_near(params['Longitude'], params['Latitude'], params['Distance'], params['Limit'])

    def locations_near(self, longitude, latitude, distance=1000, limit=5):
        """
        :param longitude:
        :param latitude:
        :param distance: The distance (in meters) of the bounds
        :param limit: How many records to return (sorted by distance)
        :return: A list of locations (as a dict) near a given coordinate.
        """

        point = GISPoint(longitude, latitude)
        locations = []
        with self.db.session_scope() as session:
            results = session.query(Location)\
                .filter(Within(Location.geom, point, distance))\
                .order_by(Distance(Location.geom, point)).limit(limit)\
                .all()

            for result in results:
                # TODO: Find out whether it is quicker to store Lat/Lng in db, or whether to compute it from the geom.
                locations.append(dict(Name=result.name, Latitude=None, Longitude=None))

        return locations
