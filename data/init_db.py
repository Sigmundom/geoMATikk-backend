'''
VIKTIG:
Les README.md for å få forklaring på hvordan bruke denne filen
'''

import json
import sys
sys.path.append("..")
from app.models import *

def init():
	with open('data/done.json', 'r') as data:
		json_file = json.load(data)

	# Slett alt som var det fra før
	db.session.query(Restaurant).delete()

	# Legg til alle restaurantene
	for restaurant in json_file:
		if restaurant['position'] == '':
			restaurant['position'] = '0 0'
		restaurant_object = Restaurant(
			restaurant['title'],
			'SRID=4326;POINT(' + restaurant['position'] + ')',
			restaurant['price'],
			restaurant['rating'],
			restaurant['description'],
			restaurant['image_url'],
			restaurant['phone'],
			restaurant['kitchen']
		)
		db.session.add(restaurant_object)
	
	# Commit
	db.session.commit()
