from flask_restful import Resource, reqparse
from keras.models import load_model
from flask import request
from utilities.crop_face import crop_face
from utilities.preprocess_image import preprocess_image
import os, base64
import pickle
import uuid
from models.child import ChildModel
import numpy as np
real_path = os.getcwd()

_child_search_parser = reqparse.RequestParser()
_child_search_parser.add_argument(
    "image",
    type=str,
    required=True,
    help="This field cannot be blank",
)
def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath


class SearchChild(Resource):
    def post(self):
        print("getting image...")
        if request.files.get("image"):
            print("image file..")
            img = request.files['image']
            img_name = str(uuid.uuid4()) + '.jpg'
            create_new_folder(os.path.join(real_path, 'temp_images'))
            saved_path = os.path.join(os.path.join(real_path, 'temp_images'), img_name)
            img.save(saved_path)
        else:
            print("base64 image..")
            data = _child_search_parser.parse_args()
            img_name = str(uuid.uuid4()) + '.jpg'
            create_new_folder(os.path.join(real_path, 'temp_images'))
            saved_path = os.path.join(os.path.join(real_path, 'temp_images'), img_name)
            with open(saved_path, "wb") as fh:
                fh.write(base64.decodebytes(data['image'].encode()))
        print("cropping face...")
        if not crop_face(saved_path, os.path.join(os.getcwd(), 'temp_croped_images')):
            return {"message": "face not found in image"}, 404
        print("finding matching image...")
        try:
            model_path = os.path.join(real_path, "model.h5")
            vgg_face_descriptor = load_model(model_path)
            svm_model = pickle.load(open(os.path.join(real_path, "svm_model.sav"), 'rb'))
            x = vgg_face_descriptor.predict(preprocess_image(os.path.join(real_path, 'temp_croped_images/1.jpg')))
            if np.max(svm_model.predict_proba(x)) < 0.6:
                return {"message": "Child not found"}, 404
            res = svm_model.predict(x)
            child = ChildModel.find_user_by_id(res[0])
            print(child)
            if child:
                return {"message": "success", "data": child.json()}, 200
            else:
                return {"message": "Child not found"}, 404
        except:
            return {"message": "Child not found"}, 404
