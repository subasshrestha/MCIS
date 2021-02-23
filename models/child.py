from database.db import db


class ChildModel(db.Model):
    __tablename__ = "childs"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    address = db.Column(db.String(80))
    parent_name = db.Column(db.String(80))
    phone = db.Column(db.String(10))
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, name, address, parent_name, phone, image):
        self.name = name
        self.address = address
        self.parent_name = parent_name
        self.phone = phone
        self.image = image

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "parent_name": self.parent_name,
            "phone": self.phone,
            "address": self.address
        }

    # Method to save user to DB
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    # Method to remove user from DB
    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    # Class method which finds user from DB by id
    @classmethod
    def find_user_by_id(cls, _id):
        return cls.query.filter_by(id=int(_id)).first()

    @classmethod
    def find_all(cls):
        children = cls.query.all()
        return [{
            "id": child.id,
            "name": child.name,
            "image": child.image,
            "parent_name": child.parent_name,
            "phone": child.phone,
            "address": child.address
        } for child in children]
