from voluptuous import *
from functools import wraps
import decimal


def validate(schema, data, **kwargs):
    return Schema(schema)(data, **kwargs)


def Datetime(msg=None, format='%Y-%m-%dT%H:%M:%S.%fZ'):

    @wraps(Datetime)
    def f(v):
        try:
            return datetime.datetime.strptime(v, format)
        except:
            raise DatetimeInvalid(msg or 'value does not match expected format %s' % format)

    return f


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
