from flask_restx import Namespace, fields


class CurrencyPairDto:
    ns = Namespace("pairs", description="Currency Pair related operations.")
    single_resp = ns.model(
        "CurrencyPair",
        {
            "id": fields.Integer,
            "code": fields.String,
            "base_code": fields.String(required=True),
            "target_code": fields.String(required=True),
        },
    )

    change_resp = ns.model(
        "CurrencyPairDataResponse",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "pair": fields.Nested(single_resp, skip_none=True),
        },
    )

    list_resp = ns.model(
        "CurrencyPairsDataResponse",
        {
            "pairs": fields.Nested(single_resp, as_list=True, skip_none=True),
        }
    )

    single_hist_resp = ns.model(
        "CurrencyRate",
        {
            "id": fields.Integer,
            "date": fields.Date(required=True),
            "rate": fields.Float(required=True),
        }
    )

    hist_resp = ns.model(
        "CurrencyPairHistoricalDataResponse",
        {
            "id": fields.Integer,
            "code": fields.String,
            "base_code": fields.String(required=True),
            "target_code": fields.String(required=True),
            "rates": fields.Nested(single_hist_resp, as_list=True, skip_none=True)
        }
    )