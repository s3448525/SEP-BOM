from flask import Blueprint
from core import web

api_comparisons_bp = Blueprint('comparisons', 'comparisons', url_prefix='/api')


@api_comparisons_bp.route('/')
@web.api_json_method
def test():
    return "hello world"
