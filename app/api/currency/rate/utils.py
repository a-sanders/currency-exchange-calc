from app.models.schemas import CurrencyRateSchema
from collections.abc import Iterable

_schema = CurrencyRateSchema()


def load_data(rates_db_obj):
    """ Load currency rate's data
    """
    data = _schema.dump(rates_db_obj, many=isinstance(rates_db_obj, Iterable))
    return data
