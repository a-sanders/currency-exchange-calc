from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.utils import err_resp, message, internal_err_resp
from app.models.currency import CurrencyPair
from app.models.schemas import CurrencyPairSchema
from .utils import load_data, load_hist_data

_schema = CurrencyPairSchema()


class CurrencyPairService:
    @staticmethod
    def get_data(pair_id):
        """ Get Currency Pair data by id """
        if not (pair := CurrencyPair.query.filter_by(id=pair_id).first()):
            return err_resp("Currency Pair not found!", "ERROR_CURRENCY_PAIR_NOT_FOUND", 404)
        try:
            data = load_data(pair)
            return data, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_hist_data(pair_id):
        """ Get Currency Pair data by id """
        if not (pair := CurrencyPair.query.filter_by(id=pair_id).first()):
            return err_resp("Currency Pair not found!", "ERROR_CURRENCY_PAIR_NOT_FOUND", 404)
        try:
            # TODO: pagination
            data = load_data(pair)
            data_rates = load_hist_data(pair.rates.all())
            data.update({"rates": data_rates})
            return data, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def update_data(pair_id, base_code, target_code, *args, **kwargs):
        """ Update Currency Pair data by id """
        if not (pair := CurrencyPair.query.filter_by(id=pair_id).first()):
            return err_resp("Currency Pair not found!", "ERROR_CURRENCY_PAIR_NOT_FOUND", 404)
        try:
            pair.base_code = base_code
            pair.target_code = target_code

            db.session.flush()
            db.session.commit()

            return "", 204
        except Exception as error:
            if error is SQLAlchemyError:
                db.session.rollback()
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_data(pair_id):
        """ Delete Currency Pair data by id """
        if not (pair := CurrencyPair.query.filter_by(id=pair_id).first()):
            return err_resp("Currency Pair not found!", "ERROR_CURRENCY_PAIR_NOT_FOUND", 404)
        try:
            db.session.delete(pair)
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
        """ Get Currency Pair list """
        pairs = CurrencyPair.query.all()
        # TODO: pagination
        try:
            data = load_data(pairs)
            return {"pairs": data}, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def post_data(base_code, target_code, *args, **kwargs):
        if pair := CurrencyPair.query.filter_by(base_code=base_code, target_code=target_code).first():
            return err_resp(f"Currency Pair {pair.code} is already exists", "ERROR_CURRENCY_PAIR_EXISTS", 409)

        try:
            new_pair = CurrencyPair(base_code=base_code, target_code=target_code)
            db.session.add(new_pair)
            db.session.flush()
            db.session.commit()

            data = load_data(new_pair)
            resp = message(True, "Currency Pair created successfully.")
            resp["pair"] = data

            return resp, 201
        except Exception as error:
            if error is SQLAlchemyError:
                db.session.rollback()
            current_app.logger.error(error)
            resp, code = internal_err_resp()
            return resp, code
