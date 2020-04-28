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
from sqlalchemy import func, cast
from geomet import wkb, wkt
from sqlalchemy.orm import defer, load_only, defaultload
import json
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.dialects import postgresql

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
    price_class_sum = db.Column(db.Integer)
    rating_sum = db.Column(db.Integer)
    description = db.Column(db.String)
    image_url = db.Column(db.String)
    phone = db.Column(db.String)
    kitchen = db.Column(postgresql.ARRAY(db.String))
    number_of_ratings = db.Column(db.Integer)

    def __init__(self, name, position, price_class, rating, description, image_url, phone, kitchen):
        self.name = name
        self.position = position
        self.price_class_sum = price_class
        self.rating_sum = rating
        self.description = description
        self.image_url = image_url
        self.phone = phone
        self.kitchen = kitchen
        self.number_of_ratings = 1

    @property
    def location(self):
        pos = wkb.loads(bytes(self.position.data))['coordinates']
        return {'latitude': pos[1], 'longitude': pos[0]}

    @property
    def rating(self):
        return self.rating_sum/self.number_of_ratings

    @property
    def price_class(self):
        return self.price_class_sum/self.number_of_ratings

    create_fields = update_fields = (['name', 'position', 'price_class', 'rating', 
        'description', 'image_url', 'phone', 'kitchen']) # List of required fields
    exclude_serialize_fields = ['position', 'kitchen', 'price_class_sum', 'rating_sum'] # List of model field names to not serialize at all.
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
    def rate_restaurant(self, restaurant_id, rating, price):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        restaurant.price_class_sum += int(price)
        restaurant.rating_sum += int(rating)
        restaurant.number_of_ratings += 1
        db.session.commit()
        return {'message': 'success'}

    @classmethod
    def fuzzy_filter(self, params):
        ALPHA = 5

        try:
            priceParams = json.loads(params['price'])
            nearbyParams = json.loads(params['nearby'])
            ratingParams = json.loads(params['rating'])
            kitchenParams = params['kitchens']
            kitchenFilter = kitchenParams.split(',') if len(kitchenParams)>0 else None
        except:
            abort(400, "Could not parse request parameters")

        if not priceParams['active'] and not nearbyParams['active'] and not nearbyParams['position'] and not ratingParams['active'] and not kitchenFilter:
            # No filter. Return all restaurants
            return Restaurant.json_list(Restaurant.query.all())

        # Get initial query with or without distance field.
        if nearbyParams['active'] and nearbyParams['position']:
            print('searching with position')
            pos = nearbyParams['position']['coords']
            point = 'SRID=4326;POINT (%f %f)' %(pos['longitude'], pos['latitude'])
            restaurants = db.session.query( Restaurant.id, 
                                            Restaurant.rating_sum, 
                                            Restaurant.price_class_sum,
                                            Restaurant.number_of_ratings,
                                            func.ST_DistanceSphere(
                                                Restaurant.position,
                                                func.ST_GeomFromText(point)).label('distance')
                                            )
        else:
            restaurants = db.session.query( Restaurant.id, 
                                            Restaurant.rating_sum, 
                                            Restaurant.price_class_sum,
                                            Restaurant.number_of_ratings,
                                        )
            
        
        
        print(kitchenFilter)

        if kitchenFilter:
            # Hard filter on kitchens
            print('Using kitchen')
            restaurants = restaurants.filter(Restaurant.kitchen.overlap(cast(kitchenFilter, db.ARRAY(db.String))))
            if restaurants.count()==0:
                return []
        
        scores = [{'id': r.id, 'score':0} for r in restaurants]
        n_restaurants = len(scores)
        sum_weights = 0

        if nearbyParams['active'] and nearbyParams['position']:
            print('Using position')
            min_distance = restaurants[0].distance
            for r in restaurants:
                if (r.distance < min_distance):
                    min_distance = r.distance

            weight = 0.2 * (nearbyParams['weight'] + 1) 
            print(weight)
            sum_weights += weight 
            print(min_distance)
            for i in range(n_restaurants):
                distance = restaurants[i].distance
                scores[i]['score'] += weight * max(0, min_distance/distance, 1-distance/5000)**ALPHA
                # scores[i]['score'] += weight * max(0, 1-(distance-min_distance)/5000)**ALPHA
                print(distance, scores[i]['score'])
        
        if ratingParams['active']:    
            print('Using rating')        
            weight = 0.2 * (ratingParams['weight'] + 1)
            sum_weights += weight 

            for i in range(n_restaurants):
                rating = restaurants[i].rating_sum/restaurants[i].number_of_ratings
                if rating:
                    scores[i]['score'] += weight * ((rating-1)/4)**ALPHA
        
        if priceParams['active']:
            print('Using price')
            weight = 0.2 * (priceParams['weight'] + 1)
            sum_weights += weight 

            preffered_value = priceParams['prefferedValue']

            for i in range(n_restaurants):
                price_class = restaurants[i].price_class_sum/restaurants[i].number_of_ratings
                if price_class:
                    score = (price_class-1)/4
                    if preffered_value == 'low':
                        score = 1 - score
                    scores[i]['score'] += weight * score**ALPHA
        
        # No sum? return all
        if sum_weights == 0:
            return Restaurant.json_list(Restaurant.query.all()) # Restaurant.json_list(restaurants)

        
        for item in scores:
            total_score = (item['score']/sum_weights)**(1/ALPHA)
            item['score'] = total_score
                    
        scores = sorted(scores, key=lambda item:item['score'], reverse=True) #Sorts on score. Decending

        best_restaurants_id = [item['id'] for item in scores[:10]]
        # print(scores[:])
        # print(scores[-1]) 
        # print (best_restaurants_id)
        restaurants = db.session.query(Restaurant).filter(Restaurant.id.in_(best_restaurants_id))
        # print(restaurants.all())

        return Restaurant.json_list(restaurants)



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
