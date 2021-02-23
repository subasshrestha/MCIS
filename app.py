from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import User, UserRegister, UserLogin, TokenRefresh
from resources.add_child import AddChild, ListChild
from resources.search_child import SearchChild
from resources.delete_child import DeleteChild
from resources.reset import Reset
from resources.image import Image
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.secret_key = "v3ry_s3cr3t_k3y"
api = Api(app)

jwt = JWTManager(app)


@jwt.expired_token_loader
def expired_token_callback():
    return jsonify(
        {
            "description": "Token has expired!",
            "error": "token_expired"
        }, 401
    )


@jwt.invalid_token_loader
def invalid_token_callback():
    return jsonify(
        {
            "description": "Signature verification failed!",
            "error": "invalid_token"
        }, 401
    )


@jwt.unauthorized_loader
def unauthorized_loader_callback(error):
    return jsonify(
        {
            "description": "Access token not found!",
            "error": "unauthorized_loader"
        }, 401
    )


@jwt.needs_fresh_token_loader
def fresh_token_loader_callback():
    return jsonify(
        {
            "description": "Token is not fresh. Fresh token needed!",
            "error": "needs_fresh_token"
        }, 401
    )


api.add_resource(User, "/api/v1/user/<int:user_id>")
api.add_resource(UserRegister, "/api/v1/register")
api.add_resource(UserLogin, "/api/v1/login")
api.add_resource(TokenRefresh, "/api/v1/refresh")
api.add_resource(AddChild, "/api/v1/addchild")
api.add_resource(ListChild, "/api/v1/child")
api.add_resource(SearchChild, "/api/v1/searchchild")
api.add_resource(Reset, "/api/v1/reset")
api.add_resource(Image, "/api/v1/image/<name>")
api.add_resource(DeleteChild, "/api/v1/delete/<child_id>")

from database.db import db

db.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response


    app.run()
