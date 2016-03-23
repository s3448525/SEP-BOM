import functools
import flask
import json
import datetime


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

        except Exception as e:
            result = dict(success=False, message="An unexpected error occurred: %s" % e)

        result = json.dumps(result, cls=JsonEncoder)
        response = flask.make_response(result)
        response.headers['Content-Type'] = 'application/json'
        return response

    return wrapper
