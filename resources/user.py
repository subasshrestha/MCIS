from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, fresh_jwt_required

from models.user import UserModel

import hashlib,re

_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    "email",
    type=str,
    required=True,
    help="This field cannot be blank"
)
_user_parser.add_argument(
    "password",
    type=str,
    required=True,
    help="This field cannot be blank"
)
_user_parser.add_argument(
    "fullname",
    type=str,
    required=True,
    help="This field cannot be blank"
)

_login_user_parser = reqparse.RequestParser()
_login_user_parser.add_argument(
    "email",
    type=str,
    required=True,
    help="This field cannot be blank"
)
_login_user_parser.add_argument(
    "password",
    type=str,
    required=True,
    help="This field cannot be blank"
)

class User(Resource):
    def get(self, user_id):
        user = UserModel.find_user_by_id(user_id)
        if user:
            return user.json()

        return {
                   "message": "User not found!"
               }, 404

    @fresh_jwt_required
    def delete(self, user_id):
        user = UserModel.find_user_by_id(user_id)
        if user:
            user.remove_from_db()
            return {
                       "message": "User deleted!"
                   }, 200

        return {
                   "message": "User not found!"
               }, 404


class UserRegister(Resource):
    def post(self):

        data = _user_parser.parse_args()

        if not 'email' in data or not 'password' in data or not 'fullname' in data:
            return {
                       "message": "Sorry, fullname, email, and password are required.",
                        "data":data
                   }, 400
        if data['email'] == '':
            return {
                "message": 'Sorry, email is required'
            },400
        if data['password'] == '':
            return {
                       "message": 'Sorry, password is required'
                   },400
        if data['fullname'] == '':
            return {
                       "message": 'Sorry, name is required'
                   },400
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.])[A-Za-z\d@$!%*?&.]{8,}$",data['password']):
            return {
                       "message": "Password must be 8 character or longer with uppercase,lowercase,numbers and special symbols"
                   }, 400

        if not len(data['fullname'].split(' ')) >= 2:
            return {
                       "message": "Please provide valid name"
                   }, 400

        if UserModel.find_user_by_email(data["email"]):
            return {
                       "message": "User exists!"
                   }, 400


        user = UserModel(data["email"], hashlib.sha256(data["password"].encode("utf-8")).hexdigest(),fullname=data['fullname'])
        user.save_to_db()
        access_token = create_access_token(identity=user.id, fresh=True)  # Puts User ID as Identity in JWT
        refresh_token = create_refresh_token(identity=user.id)  # Puts User ID as Identity in JWT

        return {
                   "access_token": access_token,
                   "refresh_token": refresh_token,
                    "email": user.email,
                    "fullname": user.full_name
               }, 200


class UserLogin(Resource):
    def post(self):
        data = _login_user_parser.parse_args()

        user = UserModel.find_user_by_email(data["email"])

        if user and user.password == hashlib.sha256(data["password"].encode("utf-8")).hexdigest():
            access_token = create_access_token(identity=user.id, fresh=True)  # Puts User ID as Identity in JWT
            refresh_token = create_refresh_token(identity=user.id)  # Puts User ID as Identity in JWT

            return {
                       "access_token": access_token,
                       "refresh_token": refresh_token,
                        "email": user.email,
                        "fullname": user.full_name
                   }, 200

        return {
                   "message": "Invalid credentials!"
               }, 401

class CurrentUser(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user_id = get_jwt_identity()  # Gets Identity from JWT
        new_token = create_access_token(identity=current_user_id, fresh=False)
        user = UserModel.find_user_by_id(current_user_id)
        return {
                   "access_token": new_token,
                   "email": user.email,
                   "fullname": user.full_name
               }, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user_id = get_jwt_identity()  # Gets Identity from JWT
        new_token = create_access_token(identity=current_user_id, fresh=False)
        return {
                   "access_token": new_token,
               }, 200