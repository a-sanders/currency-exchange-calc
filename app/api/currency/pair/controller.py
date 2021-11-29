from flask_restx import Resource, fields
from .service import CurrencyPairService
from .dto import CurrencyPairDto
from app.models.currency import CurrencyPair
from app.models.schemas import CurrencyPairSchema
from app.utils import validation_error


ns = CurrencyPairDto.ns

dto_single = CurrencyPairDto.single_resp
dto_change = CurrencyPairDto.change_resp
dto_list = CurrencyPairDto.list_resp
dto_hist = CurrencyPairDto.hist_resp

parser = ns.parser()
parser.add_argument("code", required=True, type=str, location="json")

schema = CurrencyPairSchema()

@ns.route("/<string:pair_id>")
@ns.doc(responses={404: "Currency Pair not found"},
        params={"pair_id": "The Currency Pair ID"})
class CurrencyPair(Resource):
    @ns.doc(description="Get a specific Currency Pair",
            responses={200: ("Currency Pair data successfully sent", dto_single)})
    @ns.marshal_with(dto_single, code=200)
    def get(self, pair_id):
        return CurrencyPairService.get_data(pair_id)

    @ns.doc(description="Update a specific Current Pair",
            responses={
                204: "Currency Pair updated successfully",
                400: "Malformed data or validations failed."},
            parser=parser)
    def put(self, pair_id):
        args = parser.parse_args()
        # TODO: code validation
        args["base_code"], args["target_code"] = args["code"].split('/')

        # Validate data
        if (errors := schema.validate(args)) :
            return validation_error(False, errors), 400

        return CurrencyPairService.update_data(pair_id, **args)

    @ns.doc(description="Delete a specific Currency Pair",
            responses={
                204: "Currency Pair deleted successfully",
            })
    def delete(self, pair_id):
        return CurrencyPairService.delete_data(pair_id)


@ns.route("/")
class CurrencyPairList(Resource):
    @ns.doc(description="Get Currency Pair list",
            responses={200: ("Currency Pair list successfully sent", dto_list)})
    def get(self):
        return CurrencyPairService.get_list()

    @ns.doc(description="Create new Currency Pair",
            responses={
                201: ("Currency Pair successfully created", dto_change),
                400: "Malformed data or validations failed.",
                409: "Currency Pair is already exists"},
            parser=parser)
    @ns.expect(dto_single, validate=True, code=201)
    @ns.marshal_with(dto_change, code=201)
    def post(self):
        args = parser.parse_args()
        # TODO: code validation
        args["base_code"], args["target_code"] = args["code"].split('/')

        # Validate data
        if (errors := schema.validate(args)) :
            return validation_error(False, errors), 400

        return CurrencyPairService.post_data(**args)


@ns.route("/<string:pair_id>/history")
@ns.doc(responses={404: "Currency Pair not found"},
        params={"pair_id": "The Currency Pair ID"})
class CurrencyPairHistory(Resource):
    @ns.doc(description="Get a specific Currency Pair historical data",
            responses={200: ("Currency Pair historical data successfully sent", dto_hist)})
    @ns.marshal_with(dto_hist, code=200)
    def get(self, pair_id):
        return CurrencyPairService.get_hist_data(pair_id)
