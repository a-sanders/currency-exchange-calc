from app import ma

from .currency import CurrencyPair, CurrencyRate

class CurrencyPairSchema(ma.SQLAlchemyAutoSchema):
    """ /currency/pairs/ [POST]
    """
    class Meta:
        model = CurrencyPair
        fields = ('id', 'base_code', 'target_code', 'code')


class CurrencyRateSchema(ma.Schema):
    """ /currency/rates/ [POST]
    """
    class Meta:
        model = CurrencyRate
        fields = ('id', 'date', 'rate', 'code')