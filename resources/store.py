from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import jwt_required

from db import db
from models import StoreModel
from schemas import StoreSchema


bip = Blueprint("stores", __name__, description="Operations on stores")


@bip.route("/store/<int:store_id>")
class Store(MethodView):
    @jwt_required()
    @bip.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    @jwt_required()
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()

        return {"message": "Store deleted"}


@bip.route("/store")
class StoreList(MethodView):
    @jwt_required()
    @bip.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @jwt_required()
    @bip.arguments(StoreSchema)
    @bip.response(200, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A store with that name already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the store.")

        return store, 201
