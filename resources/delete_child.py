import os
import shutil
import pandas as pd
from flask_restful import Resource
from sklearn import svm
import pickle

from models.child import ChildModel

real_path = os.getcwd()


class DeleteChild(Resource):
    @staticmethod
    def get(child_id):
        print("Deleting...")
        child = ChildModel.find_user_by_id(child_id)
        if child:
            try:
                print("deleting from csv...")
                df = pd.read_csv("data.csv", header=None)
                df = df.set_index(0)
                df = df.drop(child_id)
                df.to_csv("data.csv", header=None)
            except:
                print("error occurred")
                pass
            try:
                print("deleting from images folder")
                child_image_name = child.image
                path = os.path.join(real_path, 'images', child_image_name)
                os.remove(path)
            except:
                print("error occurred")
                pass
            try:
                print("deleting from train folder")
                path = os.path.join(os.getcwd(), 'train', str(child_id))
                shutil.rmtree(path)
            except:
                print("error occurred")
                pass
            try:
                print("deleting from croped_images folder")
                path = os.path.join(os.getcwd(), 'croped_images', str(child_id))
                shutil.rmtree(path)
            except:
                pass

            try:
                print("Training Model...")
                data = pd.read_csv(os.path.join(real_path, 'data.csv'), header=None)
                labels = data.loc[:, 0].to_numpy()
                data = data.loc[:, 1:].to_numpy()
                clf = svm.SVC(probability=True)
                clf.fit(data, labels)
                pickle.dump(clf, open("svm_model.sav", 'wb'))
            except:
                print("error occured")
                pass
            return {"message": "success"}
        else:
            print("child not found")
            return {"message": "Child Doesn't Exists."}
