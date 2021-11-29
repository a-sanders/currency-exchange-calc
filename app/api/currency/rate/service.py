import math
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from app import db, dijkstra
from app.utils import err_resp, message, internal_err_resp, pairwise
from app.models.currency import CurrencyPair, CurrencyRate
from app.models.schemas import CurrencyRateSchema
from .utils import load_data

_schema = CurrencyRateSchema()


class CurrencyRateService:
    @staticmethod
    def get_data(rate_id):
        """ Get Currency Rate data by id """
        if not (rate := CurrencyRate.query.filter_by(id=rate_id).first()):
            return err_resp("Currency Rate not found!", "ERROR_CURRENCY_RATE_NOT_FOUND", 404)
        try:
            data = load_data(rate)
            return data, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def update_data(rate_id, *args, **kwargs):
        """ Update Currency Rate data by id """
        if not (rate := CurrencyRate.query.filter_by(id=rate_id).first()):
            return err_resp("Currency Rate not found!", "ERROR_CURRENCY_RATE_NOT_FOUND", 404)
        try:
            new_date = kwargs.get('date', rate.date)
            new_pair = rate.pair

            code = kwargs.get("code", rate.code)
            if code != rate.code:
                base_code, target_code = code.split("/")
                if not (new_pair := CurrencyPair.query.filter_by(base_code=base_code, target_code=target_code).first()):
                    return err_resp(f"Currency Pair {code} not found!", "ERROR_CURRENCY_PAIR_NOT_FOUND", 404)

            new_rate = kwargs.get('rate', rate.rate)

            if obj := CurrencyRate.query.filter_by(date=new_date, pair_id=new_pair.id).first():
                if obj.id != rate.id:
                    return err_resp("Currency Rate with the specified date and code is already exists",
                                    "ERROR_CURRENCY_RATE_EXISTS", 409)

            rate.date = new_date
            rate.rate = new_rate
            rate.pair = new_pair

            db.session.flush()
            db.session.commit()

            return "", 204
        except Exception as error:
            if error is SQLAlchemyError:
                db.session.rollback()
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_data(rate_id):
        """ Delete Currency Rate data by id """
        if not (rate := CurrencyRate.query.filter_by(id=rate_id).first()):
            return err_resp("Currency Rate not found!", "ERROR_CURRENCY_RATE_NOT_FOUND", 404)
        try:
            db.session.delete(rate)
            db.session.flush()
            db.session.commit()
            return "", 204
        except Exception as error:
            if error is SQLAlchemyError:
                db.session.rollback()
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_list():
        """ Get Currency Rate list """
        rates = CurrencyRate.query.all()
        # TODO: pagination
        try:
            data = load_data(rates)
            return {"rates": data}, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def post_data(date, rate, code, *args, **kwargs):
        """ Create new Currency Rate """
        base_code, target_code = code.split("/")
        if not (pair := CurrencyPair.query.filter_by(base_code=base_code, target_code=target_code).first()):
            return err_resp(f"Currency Pair {code} not found!", "ERROR_CURRENCY_PAIR_NOT_FOUND", 404)

        if CurrencyRate.query.filter_by(date=date, pair_id=pair.id).first():
            return err_resp("Currency Rate is already exists", "ERROR_CURRENCY_RATE_EXISTS", 409)

        try:
            new_rate = CurrencyRate(date=date, rate=rate, pair=pair)
            db.session.add(new_rate)
            db.session.flush()
            db.session.commit()

            data = load_data(new_rate)
            resp = message(True, "Currency Rate created successfully.")
            resp["rate"] = data

            return resp, 201
        except Exception as error:
            if error is SQLAlchemyError:
                db.session.rollback()
            current_app.logger.error(error)
            resp, code = internal_err_resp()
            return resp, code

    @staticmethod
    def calculate(base_code, target_code, date):
        """ Calculate Currency Rate by date and code """
        if not (rates := CurrencyRate.query.filter_by(date=date).all()):
            return err_resp("Currency Rate is not found for the specified date", "ERROR_CURRENCY_RATE_NOT_FOUND", 404)

        data = None
        if pair := CurrencyPair.query.filter_by(base_code=base_code, target_code=target_code).first():
            if rate := pair.rates.filter_by(date=date).first():
                data = load_data(rate)
        elif pair := CurrencyPair.query.filter_by(base_code=target_code, target_code=base_code).first():
            if rate := pair.rates.filter_by(date=date).first():
                rate.rate = 1 / rate.rate
                data = load_data(rate)
        if data:
            return data, 200

        symbols = db.session.query(CurrencyPair.base_code).union(db.session.query(CurrencyPair.target_code)).all()
        symbols = dict.fromkeys(set().union(*symbols))

        if base_code not in symbols:
            return err_resp(f"Currency symbol {base_code} is unknown", "ERROR_CURRENCY_SYMBOL_NOT_FOUND", 404)

        if target_code not in symbols:
            return err_resp(f"Currency symbol {target_code} is unknown", "ERROR_CURRENCY_SYMBOL_NOT_FOUND", 404)

        nodes = []
        for key in symbols:
            symbols[key] = dijkstra.Node(key)
            nodes.append(symbols[key])

        w_graph = dijkstra.Graph.create_from_nodes(nodes)

        _rates = dict()
        for rate in rates:
            w_graph.connect(symbols[rate.pair.base_code], symbols[rate.pair.target_code], rate.rate)
            _rates[(rate.pair.base_code, rate.pair.target_code)] = rate.rate

        rc = None
        for weight, node in w_graph.dijkstra(symbols[base_code]):
            path = [n.data for n in node]
            if len(path) == 1:
                continue
            if path[-1] == target_code:
                rc = dict(path=path)
                break
        if rc:
            r = 1.0
            for c0, c1 in pairwise(rc['path']):
                if (c0, c1) in _rates:
                    r *= _rates[(c0, c1)]
                elif (c1, c0) in _rates:
                    r /= _rates[(c1, c0)]

            rc['rate'] = r
            rc['date'] = date
            rc['code'] = f"{base_code}/{target_code}"
            return rc, 200
        else:
            return err_resp("Currency Rate cannot be calculated", "ERROR_CURRENCY_RATE_NOT_AVAILABLE", 404)
