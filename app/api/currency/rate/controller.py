from flask_restx import Resource, fields, inputs
from .service import CurrencyRateService
from .dto import CurrencyRateDto
from app.models.currency import CurrencyRate
from app.models.schemas import CurrencyRateSchema
from app.utils import validation_error


ns = CurrencyRateDto.ns

dto_single = CurrencyRateDto.single_resp
dto_change = CurrencyRateDto.change_resp
dto_list = CurrencyRateDto.list_resp

parser = ns.parser()
parser.add_argument("code", required=True, type=str, location="json")
parser.add_argument("rate", required=True, type=float, location="json")
parser.add_argument("date", required=True, type=inputs.date_from_iso8601, location="json")

calc_parser = ns.parser()
calc_parser.add_argument("code", required=True, type=str, location="args")
calc_parser.add_argument("date", required=True, type=inputs.date_from_iso8601, location="args")

schema = CurrencyRateSchema()

@ns.route("/<string:rate_id>")
@ns.doc(responses={404: "Currency Rate not found"},
        params={"rate_id": "The Currency Rate ID"})
class CurrencyRate(Resource):
    @ns.doc(description="Get a specific Currency Rate",
            responses={200: ("Currency Rate data successfully sent", dto_single)})
    @ns.marshal_with(CurrencyRateDto.single_resp, code=200)
    def get(self, rate_id):
        return CurrencyRateService.get_data(rate_id)

    @ns.doc(description="Update a specific Current Rate",
            responses={
                204: "Currency Rate updated successfully",
                400: "Malformed data or validations failed."},
            parser=parser)
    def put(self, rate_id):
        args = parser.parse_args()

        # Validate data
        if (errors := schema.validate(args)) :
            return validation_error(False, errors), 400

        return CurrencyRateService.update_data(rate_id, **args)

    @ns.doc(description="Delete a specific Currency Rate",
            responses={
                204: "Currency Rate deleted successfully",
            })
    def delete(self, rate_id):
        return CurrencyRateService.delete_data(rate_id)


@ns.route("/<string:base_code>/<string:target_code>/<string:date>")
class CurrencyRateCalc(Resource):
    @ns.doc(description="Calculate rate for given currency pair at given date. "
                        "In case there is no such currency pair, calculate it by using others.",
            responses={
                200: ("Currency Rate data successfully sent", dto_single),
                404: "Currency Rate not found"
            })
    def get(self, base_code, target_code, date):
        return CurrencyRateService.calculate(base_code, target_code, date)


@ns.route("/")
class CurrencyRateList(Resource):
    @ns.doc(description="Get Currency Rate list",
            responses={200: ("Currency Rate list successfully sent", dto_list)})
    def get(self):
        return CurrencyRateService.get_list()

    @ns.doc(description="Create new Currency Rate",
            responses={
                201: ("Currency Rate successfully created", dto_change),
                400: "Malformed data or validations failed.",
                409: "Currency Rate is already exists"},
            parser=parser)
    @ns.expect(CurrencyRateDto.single_resp, validate=True, code=201)
    @ns.marshal_with(dto_change, code=201)
    def post(self):
        args = parser.parse_args()

        # Validate data
        if (errors := schema.validate(args)) :
            return validation_error(False, errors), 400

        return CurrencyRateService.post_data(**args)
