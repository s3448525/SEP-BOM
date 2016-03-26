import functools
import flask
import json
import datetime
from core.validator import MultipleInvalid


def get_db():
    import feva
    db = getattr(flask.g, 'db', None)
    if db is None:
        db = feva.db
        setattr(flask.g, 'db', db)
    return db


def get_post_data():
    return flask.request.get_json()


def get_parameters():
    return flask.request.args


class JsonEncoder(json.JSONEncoder):
    """
    Customised JSON encoder for any custom objects there may be.
    Add below:
    """
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def api_json_method(f):
    """
    A wrapper which forces a json response.
    Errors will also be returned in json.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)

            if not isinstance(result, dict):
                result = dict(data=result, success=True)
            elif 'success' not in result:
                result['success'] = True

        except MultipleInvalid as e:
            errors = []
            for error in e.errors:
                errors.append('%s: %s' % (error.msg, error.path[-1]))
            result = dict(success=False, errors=errors, message='Validation Error')

        except Exception as e:
            result = dict(success=False, message="An unexpected error occurred: %s" % e)

        result = json.dumps(result, cls=JsonEncoder)
        response = flask.make_response(result)
        response.headers['Content-Type'] = 'application/json'
        return response

    return wrapper
