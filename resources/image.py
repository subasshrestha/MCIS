from flask_restful import Resource
from flask import send_file
from os import path


class Image(Resource):
    def get(self, name):
        if path.exists('images/' + name):
            return send_file('images/' + name)
        else:
            return None
