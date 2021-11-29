from flask_restx import Api
from flask import Blueprint

api_v1_bp = Blueprint("api", __name__, url_prefix="/api/v1/currency")

api = Api(api_v1_bp,
          version="1.0",
          title="Currency Exchange Calculator API",
          description="API service for currency exchange calculator",)


# Import controller APIs as namespaces.
from .currency import pair
api.add_namespace(pair.ns)

from .currency import rate
api.add_namespace(rate.ns)