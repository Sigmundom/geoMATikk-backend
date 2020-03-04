import json

import sys
sys.path.append("..")

from app.models import *

def init():
	with open('data/test.json', 'r') as data:
		json_file = json.load(data)

	for restaurant in json_file:
		if restaurant['position'] == '':
			restaurant['position'] = '0 0'
		restaurant_object = Restaurant(
			restaurant['title'],
			'SRID=4326;POINT(' + restaurant['position'] + ')',
			None,
			None,
			restaurant['description'],
			restaurant['image_url'],
			restaurant['phone']
		)
		db.session.add(restaurant_object)
	
	db.session.commit()
