from voluptuous import *


def validate(schema, data, **kwargs):
    return Schema(schema)(data, **kwargs)
