import json
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        print("Encountered some data  :", data)


with open('l1ecv_content.json', 'r') as n:
	json_file = json.load(n)




'''
# Print ut alle restauranter, barer og kafeer
print('Restaunter:')
for data in json_file[2]['data']:

	if data['catid'] == '39' and data['state'] == '1':
		print(data['title'] + ' : ')

print('\n\nBar&Kafe:')
for data in json_file[2]['data']:
	if data['catid'] == '55' and data['state'] == '1':
		print(data['title'] + ' : ')
'''


'''
Vil ha:
title
introtext (finns mie inni denne)
image_fulltext (from images)
xreference (from metadata)
'''

parser = MyHTMLParser()

for data in json_file[2]['data']:
	if data['catid'] in ['39', '55']:
		eating_place = {}

		# title
		eating_place['title'] = data['title']

		# image_url
		eating_place['image_url'] = json.loads(data['images'])['image_fulltext']

		# position
		xreference = json.loads(data['metadata'])['xreference']
		eating_place['position'] = xreference.replace(',',' ')

		html_test = "<p>Michelinstjerne-belønnet restaurant på Lilleby, like nordøst for Trondheim sentrum. Her serveres ikke mat á la carte. I stedet bestemmer kjøkkenet hvilke smaker som skal rendyrkes, med utgangspunkt i råvarene som finnes på en gitt dag. Kokkene komponerer hver dag en unik kombinasjon av retter og vin. Man kan til vanlig velge mellom tre og fem retter. Credo var sammen med Fagn de to første restaurantene i Trondheim som mottok en Michelin-stjerne i februar 2019.<\/p>\r\n<h4>Kontaktinfo<\/h4>\r\n<p>Adresse: Ladeveien 9, Trondheim<\/p>\r\n<p>Telefon : <a href=\"tel:+47 954 37 028\">+47 954 37 028<\/a><\/p>\r\n<p>E-post: <a class=\"dark_gray partner-hover mailto\" href=\"mailto:credo@restaurantcredo.no\" rel=\"noindex, nofollow\">Send en e-post <\/a><\/p>\r\n<p>Nettsted: <a class=\"dark_gray url partner-hover\" href=\"http:\/\/www.restaurantcredo.no\" target=\"_blank\" rel=\"noindex, nofollow noopener noreferrer\">Besøk websiden <\/a><\/p>"
		parser.feed(html_test)

		# xreference = data['metadata'].keys() # .replace('\\','')
		# print(json.loads(data['metadata'])['xreference'].replace(',',' '))
		break
