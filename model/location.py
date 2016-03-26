from model.schema import Location
from core.distance_helpers import GISPoint, Within, Distance


class LocationManager(object):

    def __init__(self, db):
        self.db = db

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
