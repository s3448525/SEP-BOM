'''
convert location string into latitude and longitude
'''
from geoalchemy2.elements import WKTElement
import struct
from binascii import unhexlify

wkb_point = "0101000020E610000031ED9BFBAB27194058C7F143A5854A40"
coords = struct.unpack_from('dd', unhexlify(str(wkb_point)), 5)


print (coords[1], coords[0])
