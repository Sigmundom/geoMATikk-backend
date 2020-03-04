"""This file will store the different web adresses you have, and works as a directory too look up the different parts
 of the application. This calls the @app.route function in flask, and checks for the input navigation keyword. Remember
 that if you dont place any redirection to a HTML file, the HTML file will not rendered*

 *There are ways of linking HTML files directly in text on other HTML files, but this is not recomended practice in
 flask """

from flask import render_template, request
from app import app
from app.models import *


@app.route('/')
def index():
    return {'hello': 'world'}

    
@app.route('/restaurant/<int:ID>', methods=['GET', 'PUT', 'DELETE', 'POST'])
@app.route('/restaurant', methods=['GET', 'POST'])
def route_restaurant_all(ID=None):
    return Restaurant.get_delete_put_post(ID)

@app.route('/restaurant/filter', methods=['GET'])
def route_restaurant_search():
    params = request.args
    # Default: Returns all restaurants if no filters
    query = Restaurant.query.all()
    if params:
        if params['search']:
            query = Restaurant.query.filter(Restaurant.name.ilike('%' + params['search'] + '%'))
       

    return Restaurant.json_list(query)

@app.route('/user/<int:ID>', methods=['GET', 'PUT', 'DELETE', 'POST'])
@app.route('/user', methods=['GET', 'POST'])
def route_user_all(ID=None):
    return User.get_delete_put_post(ID)

@app.route('/visit', methods=['POST'])
def route_visit():
    userID = request.data['userID']
    restaurantID = request.data['restaurantID']
    user = User.query.get_or_404(userID)
    restaurant = Restaurant.query.get_or_404(restaurantID)
    user.visited_restaurants.append(restaurant)
    db.session.add(user)
    db.session.commit()
    return 'Success'
    
# @app.route('/user', methods=['GET'])
# def user():
#     return User.json_list(User.query.all())
    
