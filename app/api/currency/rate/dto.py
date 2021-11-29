from flask_restx import Namespace, fields


class CurrencyRateDto:
    ns = Namespace("rates", description="Currency Rate related operations.")
    single_resp = ns.model(
        "CurrencyRate",
        {
            "id": fields.Integer,
            "date": fields.Date(required=True),
            "rate": fields.Float(required=True),
            "code": fields.String(required=True)
        },
    )

    change_resp = ns.model(
        "CurrencyRateDataResponse",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "rate": fields.Nested(single_resp, skip_none=True),
        },
    )

    list_resp = ns.model(
        "CurrencyRatesDataResponse",
        {
            "rates": fields.Nested(single_resp, as_list=True, skip_none=True),
        }
    )