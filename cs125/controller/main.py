from sanic.response import json, text
from sanic import Blueprint
from sanic.views import HTTPMethodView
from sanic.exceptions import InvalidUsage, NotFound

from models.model import Report
from db import db_service
from .exception.exceptions import QuotaError
import log
import config

logger = log.get_logger(__name__)
LATEST = "latest"


def str_to_bool(string):
    """
    Parses string into boolean
    """
    string = string.lower()
    return True if string == "true" or string == "yes" else False

class StoreView(HTTPMethodView):
    def options(self, request):
        return json({})

    def post(self, request):
        #TODO recycle old generated emails
        form = request.form
        return json({'accounts': None, "count": 1})


class FetchView(HTTPMethodView):
    def delete(self, request, id):
        id = parse_id(id)
        if (id is None):
            raise InvalidUsage('id must be a valid email address or kitid')
        return json({})

bp = Blueprint('mail')
bp.add_route(StoreView(), '/store/<id>')
bp.add_route(FetchView(), '/fetch/<id>')
