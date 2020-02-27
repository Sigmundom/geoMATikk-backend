"""This is an example of a model, containing a few fields. Use this as a blueprint of your future models.

The tablename tag is used for defining the name of the model in the database. The fields contains the information that
you want to store in the model.

The __init__ function is used by flask to initialize each model instance when you create it. It will be transform the
values you send to the model blueprint into a model instance.

The __repr__ function wil return the id of the model instance, useful for queries and sorting

The serialize function is needed for placing the now created model instance into the database. It wil give the output
too the flask framework, which will handle the database actions.

Useful links:
https://pypi.org/project/flask-serialize/
https://github.com/Martlark/flask-serialize/blob/master/flask_serialize/flask_serialize.py
"""

from app import db
from flask_serialize import FlaskSerializeMixin
from geoalchemy2 import Geometry
from geomet import wkb

FlaskSerializeMixin.db = db

RestaurantVisit = db.Table('RestaurantVisist',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurant.id'))
)

class User(db.Model, FlaskSerializeMixin):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String)

    visited_restaurants = db.relationship('Restaurant', secondary=RestaurantVisit, lazy=True,
        backref=db.backref('user', lazy=True))

    create_fields = update_fields = ['name'] # List of required fields
    exclude_serialize_fields = [] # List of model field names to not serialize at all.
    relationship_fields = ['visited_restaurants'] # Add any relationship property name here to be included in serialization.



    def __repr__(self):
        return 'id: {}, name: {}'.format(self.id, self.name)


class Restaurant(db.Model, FlaskSerializeMixin):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String)
    position = db.Column(Geometry(geometry_type="POINT", srid=4326),)
    price_class = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    description = db.Column(db.String)
    image_url = db.Column(db.String)
    phone = db.Column(db.String)

    @property
    def location(self):
        pos = wkb.loads(bytes.fromhex(str(self.position)))['coordinates']
        return {'latitude': pos[0], 'longitude': pos[1]}

    create_fields = update_fields = (['name', 'position', 'price_class', 'rating', 
        'description', 'image_url', 'phone']) # List of required fields
    exclude_serialize_fields = ['position'] # List of model field names to not serialize at all.
    relationship_fields = [] # Add any relationship property name here to be included in serialization.


    # checks if Flask-Serialize can delete
    def can_delete(self):
        # Add constraints here:
        if False:
            return Exception()

    # # checks if Flask-Serialize can create/update
    def verify(self, create=False):
        # Checks if all fields in create_fields is given:
        if create:
            for field in self.create_fields:
                if len(getattr(self,field) or '') < 1:
                    raise Exception('Missing attribute: {}'.format(field))

    def __repr__(self):
        return 'id: {}, name: {}'.format(self.id, self.name)




# Template Model
'''
class Model(db.Model, FlaskSerializeMixin):
    __tablename__ = 'models'

    id = db.Column(db.Integer, primary_key=True, index=True)

    create_fields = update_fields = [] # List of required fields
    exclude_serialize_fields = [] # List of model field names to not serialize at all.
    relationship_fields = [] # Add any relationship property name here to be included in serialization.

    def __repr__(self):
        return '<id {}>'.format(self.id)

    # checks if Flask-Serialize can delete
    def can_delete(self):
        # Add constraints here:
        if False:
            return Exception()

    # # checks if Flask-Serialize can create/update
    def verify(self, create=False):
        # Checks if all fields in create_fields is given:
        for field in self.create_fields:
            if len(getattr(self,field) or '') < 1:
                raise Exception('Missing attribute: {}'.format(field))

'''
