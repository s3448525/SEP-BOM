from geoalchemy2.elements import WKTElement
from geoalchemy2 import func
import re
import struct
from binascii import unhexlify


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


class _AsLatLon(object):

    def __call__(self, point):
        return func.ST_AsText(point)

Within = _Within()
GISPoint = _GISPoint()
Distance = _Distance()
AsLatLon = _AsLatLon()

point_regex = re.compile(r'POINT\((-?\d+\.\d+) (-?\d+\.\d+)\)')


def decode_point(point):
    return point_regex.findall(point)[0]


def unpack_wkb_point(wkb_point):
    coords = struct.unpack_from('dd', unhexlify(str(wkb_point)), 5)
    return (coords[1], coords[0])
