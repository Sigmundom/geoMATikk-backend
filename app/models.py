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

from app import db, app
from flask_serialize import FlaskSerializeMixin
from geoalchemy2 import Geometry
from geomet import wkb
import json
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

FlaskSerializeMixin.db = db

RestaurantVisit = db.Table('RestaurantVisist',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurant.id'))
)

class User(db.Model, FlaskSerializeMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True)
    password_hash = db.Column(db.String(128))

    visited_restaurants = db.relationship('Restaurant', secondary=RestaurantVisit, lazy=True,
        backref=db.backref('user', lazy=True))

    create_fields = update_fields = ['name'] # List of required fields
    exclude_serialize_fields = [] # List of model field names to not serialize at all.
    relationship_fields = ['visited_restaurants'] # Add any relationship property name here to be included in serialization.

    def __repr__(self):
        return 'id: {}, username: {}'.format(self.id, self.username)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration = 15778463): #15 778 463 seconds = 6 months
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user


class Restaurant(db.Model, FlaskSerializeMixin):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String)
    position = db.Column(Geometry(geometry_type="POINT", srid=4326))
    price_class = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    description = db.Column(db.String)
    image_url = db.Column(db.String)
    phone = db.Column(db.String)

    def __init__(self, name, position, price_class, rating, description, image_url, phone):
        self.name = name
        self.position = position
        self.price_class = price_class
        self.rating = rating
        self.description = description
        self.image_url = image_url
        self.phone = phone

    @property
    def location(self):
        pos = wkb.loads(bytes(self.position.data))['coordinates']
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

    @classmethod
    def fuzzy_filter(self, params):
        def normalize_array(array):
            maximum = min(array)
            norm = [float(i)/maximum for i in array]
        # Default: Returns all restaurants if no filters
        restaurants = Restaurant.query

        try:
            priceParams = json.loads(params['price'])
            nearbyParams = json.loads(params['nearby'])
            ratingParams = json.loads(params['rating'])
        except:
            print("Could not parse request parameters")


        if params:
            if params['search']:
                restaurants = restaurants.filter(Restaurant.name.ilike('%' + params['search'] + '%'))
            if nearbyParams['active'] and nearbyParams['position']:
                pos = nearbyParams['position']['coords']
                point = 'SRID=4326;POINT (%f %f)' %(pos['latitude'], pos['longitude'])
                
                restaurants = restaurants.add_columns(Restaurant.position.distance_centroid(point).label("distance")).filter("distance" < 5000)
                distances = [r.distance for r in restaurants]
                min_distance = min(distances)
                weight = 0.2 * (nearbyParams['weight'] + 1)
                distances = [weight * max(min_distance/i, 1-i/5000) for i in distances]

            if ratingParams['active']:
                weight = 0.2 * (ratingParams['weight'] + 1)

            if priceParams['active']:
                for r in restaurants:
                    print(r.price_class)


        return restaurants




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
