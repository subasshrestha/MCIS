
from database.db import db


class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80))
    password = db.Column(db.String())
    full_name = db.Column(db.String())
    created_at = db.Column(db.DateTime(),server_default=db.func.now())
    role = db.Column(db.String(),default='GENERAL')
    updated_at = db.Column(db.DateTime(),server_default=db.func.now(),server_onupdate=db.func.now())


    def __init__(self, email, password,fullname):
        self.email = email
        self.password = password
        self.full_name = fullname

    def json(self):
        return {
                   "id": self.id,
                   "email": self.email,
                   "full_name": self.full_name
               }, 200

    # Method to save user to DB
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    # Method to remove user from DB
    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    # Class method which finds user from DB by username
    @classmethod
    def find_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    # Class method which finds user from DB by id
    @classmethod
    def find_user_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()