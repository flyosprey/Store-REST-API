from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import get_jwt_identity, create_refresh_token, create_access_token, jwt_required, get_jwt
from sqlalchemy import or_

from db import db
from blocklist import BLOCKLIST
from models import UserModel
from schemas import UserSchema, UserRegisterSchema
from tasks import send_user_registration_email

bip = Blueprint("Users", "users", description="Operations on users")


@bip.route("/register")
class UserRegister(MethodView):
    @bip.arguments(UserRegisterSchema)
    def post(self, user_data):
        if UserModel.query.filter(
                or_(UserModel.username == user_data["username"], UserModel.email == user_data["email"])
        ).first():
            abort(409, message="A user with that username or email already exists.")

        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )
        db.session.add(user)
        db.session.commit()

        current_app.queue.enqueue(send_user_registration_email, user.email, user.username)

        return {"message": "User created successfully."}, 201


@bip.route("/login")
class UserLogin(MethodView):
    @bip.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}
        abort(401, message="Invalid credentials.")


@bip.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        # CREATE JUST ONE NON-FRESH TOKEN FOR ONE FRESH TOKEN
        # jti = get_jwt()["jti"]
        # BLOCKLIST.add(jti)
        return {"access_token": new_token}


@bip.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out."}


@bip.route("/user/<int:user_id>")
class User(MethodView):
    @jwt_required()
    @bip.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @jwt_required()
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200
