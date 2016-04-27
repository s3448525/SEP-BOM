from voluptuous import *
from functools import wraps
import decimal


def validate(schema, data, **kwargs):
    return Schema(schema)(data, **kwargs)


def Decimal(msg=None):

    @wraps(Decimal)
    def f(v):
        try:
            return decimal.Decimal(v)
        except:
            try:
                return decimal.Decimal(str(v))
            except:
                raise Invalid(msg and msg or "Could not convert to decimal")
    return f


# TODO: make sure these are correct ranges
Latitude = Decimal
Longitude = Decimal
