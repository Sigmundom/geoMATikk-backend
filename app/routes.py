"""This file will store the different web adresses you have, and works as a directory too look up the different parts
 of the application. This calls the @app.route function in flask, and checks for the input navigation keyword. Remember
 that if you dont place any redirection to a HTML file, the HTML file will not rendered*

 *There are ways of linking HTML files directly in text on other HTML files, but this is not recomended practice in
 flask """

from flask import render_template, request, jsonify, abort, url_for, g
from app import app
from app.models import *


@app.route('/')
def index():
    return {'hello': 'world'}

#Restaurants ----------------------------------

@app.route('/restaurant/<int:ID>', methods=['GET', 'PUT', 'DELETE', 'POST'])
@app.route('/restaurant', methods=['GET', 'POST'])
def route_restaurant_all(ID=None):
    return Restaurant.get_delete_put_post(ID)

@app.route('/restaurant/filter', methods=['GET'])
def route_restaurant_search():
    return Restaurant.fuzzy_filter(request.args)


# Users --------------------------------------

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/users', methods = ['POST'])
def new_user():
    username = request.data['username']
    password = request.data['password']
    if username is None or password is None:
        abort(400, 'Missing arguments') # missing arguments
    if User.query.filter_by(username = username).first() is not None:
        abort(400, 'Exisitng user') # existing user
    user = User(username = username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    print(url_for('get_user', id = user.id, _external = True))
    token =  user.generate_auth_token()
    return jsonify({ 'username': user.username, 'token': token.decode('ascii') }), 201, {'Location': url_for('get_user', id = user.id, _external = True)}

@app.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({'username': user.username})

@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'username': g.user.username, 'token': token.decode('ascii') })

@app.route('/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })

    
# @app.route('/user/<int:ID>', methods=['GET', 'PUT', 'DELETE', 'POST'])
# @app.route('/user', methods=['GET', 'POST'])
# def route_user_all(ID=None):
#     return User.get_delete_put_post(ID)


# Visit --------------------------

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
    
