from geoalchemy2.elements import WKTElement
from geoalchemy2 import func


class _GISPoint(object):
    def __call__(self, longitude, latitude):
        return WKTElement('POINT(%.7f %.7f)' % (longitude, latitude), srid=4326)


class _Within(object):
    """
    Helper for the geoalchemy ST_DWithin function.
    """

    def __call__(self, source, dest, distance):
        """

        :param source: The source location (generally a database record)
        :param dest: the point to measure
        :param distance: how far the bounds are
        :return: an sqlalchemy func object
        """
        return func.ST_DWithin(source, dest, distance)

class _Distance(object):

    def __call__(self, source, dest):
        return func.ST_Distance(source, dest)

Within = _Within()
GISPoint = _GISPoint()
Distance = _Distance()
