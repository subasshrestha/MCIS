import os
from flask_restful import Resource
import shutil
from database.db import db

def remove_file(path):
    try:
        os.remove(path)
    except:
        pass


def remove_directory(path):
    try:
        shutil.rmtree(path)
    except:
        pass


class Reset(Resource):
    def get(self):
        remove_file('data.csv')
        remove_file('data.db')
        remove_file('svm_model.sav')
        remove_directory('train')
        remove_directory('croped_images')
        remove_directory('images')
        remove_directory('temp_croped_images')
        remove_directory('temp_images')
        db.create_all()
        return {"msg": "success"}, 200
