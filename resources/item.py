from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from schemas import ItemSchema, ItemUpdateSchema
from sqlalchemy.exc import SQLAlchemyError

from models import ItemModel
from db import db


bip = Blueprint("items", __name__, description="Operations on items")


@bip.route("/item/<int:item_id>")
class Item(MethodView):
    @jwt_required()
    @bip.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self, item_id):
        # JUST AN EXAMPLE
        # jwt = get_jwt()
        # if not jwt["is_admin"]:
        #     abort(401, message="Admin privilege required.")
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()

        return {"message": "Item deleted"}

    @jwt_required(fresh=True)
    @bip.arguments(ItemUpdateSchema)
    @bip.response(200, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item


@bip.route("/item")
class ItemList(MethodView):
    @jwt_required()
    @bip.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required()
    @bip.arguments(ItemSchema)
    @bip.response(200, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item.")

        return item, 201
