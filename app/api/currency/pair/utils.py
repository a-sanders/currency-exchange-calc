from app.models.schemas import CurrencyPairSchema, CurrencyRateSchema
from collections.abc import Iterable

_schema = CurrencyPairSchema()
_schema_hist = CurrencyRateSchema()

def load_data(pairs_db_obj):
    """ Load currency pair's data
    """
    data = _schema.dump(pairs_db_obj, many=isinstance(pairs_db_obj, Iterable))
    return data


def load_hist_data(rates_db_obj):
    """ Load currency rate's data
    """
    data = _schema_hist.dump(rates_db_obj, many=isinstance(rates_db_obj, Iterable))
    return data
