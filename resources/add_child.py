from flask_restful import Resource, reqparse
from flask import request
import os, requests
import base64
from keras.models import load_model
from utilities.crop_face import crop_face
from utilities.preprocess_image import preprocess_image
import glob
import pandas as pd
from sklearn import svm
import pickle
from werkzeug.utils import secure_filename
import uuid
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from models.child import ChildModel

real_path = os.getcwd()

_child_parser = reqparse.RequestParser()
_child_parser.add_argument(
    "name",
    type=str,
    required=True,
    help="This field cannot be blank",
)
_child_parser.add_argument(
    "image",
    type=str,
    required=True,
    help="This field cannot be blank",
)


def save_to_csv(data, key):
    df = pd.DataFrame(data)
    df.index = [key]
    df.to_csv(os.path.join(real_path, 'data.csv'), mode='a', header=False)


def train(id):
    model_path = os.path.join(real_path, "model.h5")
    vgg_face_descriptor = load_model(model_path)
    if not os.path.exists(os.path.join(os.getcwd(), 'data.csv')):
        a = vgg_face_descriptor.predict(preprocess_image(os.path.join(real_path, 'first_image/random.jpg')))
        save_to_csv(a, 'first_image')
    for file in glob.glob(os.path.join(real_path, 'train/' + str(id) + '/*.jpg')):
        a = vgg_face_descriptor.predict(preprocess_image(file))
        save_to_csv(a, str(id))
    data = pd.read_csv(os.path.join(real_path, 'data.csv'), header=None)
    labels = data.loc[:, 0].to_numpy()
    data = data.loc[:, 1:].to_numpy()
    clf = svm.SVC(probability=True)
    clf.fit(data, labels)
    pickle.dump(clf, open("svm_model.sav", 'wb'))


def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath


class ListChild(Resource):
    @staticmethod
    def get():
        children = ChildModel.find_all()
        return children, 200


class AddChild(Resource):
    @staticmethod
    def post():
        print("saving image...")
        if request.files.get("image"):
            print("image file..")
            if not request.form.get("name"):
                return {"message":"Name field cant be empty."}
            data = {"name": request.form.get("name")}
            img = request.files['image']
            img_name = str(uuid.uuid4()) + '.jpg'
            create_new_folder(os.path.join(real_path, 'images'))
            saved_path = os.path.join(os.path.join(real_path, 'images'), img_name)
            img.save(saved_path)
        else:
            print("base64 image")
            data = _child_parser.parse_args()
            img_name = str(uuid.uuid4()) + '.jpg'
            create_new_folder(os.path.join(real_path, 'images'))
            saved_path = os.path.join(os.path.join(real_path, 'images'), img_name)
            with open(saved_path, "wb") as fh:
                fh.write(base64.decodebytes(data['image'].encode()))

        # section for saving child info into database
        child = ChildModel(data['name'], img_name)
        child.save_to_db()

        print("cropping face...")
        id = child.id  # get this value from database(child record id)
        if not crop_face(saved_path, os.path.join(os.getcwd(), 'croped_images/' + str(id))):
            return {"message": "face not found in image"}, 404

        print("generating multiple images...")
        # generating multiple image from uploaded image
        datagen = ImageDataGenerator(
            rotation_range=40,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest')
        img = load_img(os.path.join(os.getcwd(), 'croped_images/' + str(id) + '/1.jpg'))  # this is a PIL image
        x = img_to_array(img)  # this is a Numpy array with shape (3, 150, 150)
        x = x.reshape((1,) + x.shape)  # this is a Numpy array with shape (1, 3, 150, 150)
        # the .flow() command below generates batches of randomly transformed images
        # and saves the results to the `preview/` directory
        if not os.path.exists(os.path.join(os.getcwd(), 'train/' + str(id))):
            os.makedirs(os.path.join(os.getcwd(), 'train/' + str(id)))
        i = 0
        for batch in datagen.flow(x, batch_size=1,
                                  save_to_dir=os.path.join(os.getcwd(), 'train/' + str(id)), save_prefix='image',
                                  save_format='jpg'):
            i += 1
            if i > 5:
                break

        # training
        print("trainning...")
        train(id)
        return {"message": "success"}
