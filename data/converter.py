import json
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        # initialize the base class
        HTMLParser.__init__(self)
        self.mode = 'description'
        self.info = {}


    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag)

        hrefs = [val[1] for indx, val in enumerate(attrs) if val[0] == 'href']
        if len(hrefs) > 0:
            if hrefs[0].startswith('http') or hrefs[0].startswith('www'):
                self.mode = 'web'
            elif hrefs[0].startswith('mailto'):
                self.mode = 'email'
            elif hrefs[0].startswith('tel'):
                self.mode = 'phone'

        # if tag == 'p':
        #     self.mode == 'header'
        #     self.mode = 'description'
        #    print('a.data:', data)
        if self.mode == 'email':
            if not 'email' in self.info:
                # print('Mail:', attrs)
                # finn objektet med 'href' som attrs[]
                mails = [val[1] for indx, val in enumerate(attrs) if val[0] == 'href']
                if len(mails) > 0:
                    if mails[0].startswith('mailto:'):
                        mails[0] = mails[0][len('mailto:'):]
                    self.info['email'] = mails[0]


        elif self.mode == 'web':
            if not 'web' in self.info:
                # print('Web:', attrs)
                # finn objektet med 'href' som attrs[]
                webs = [val[1] for indx, val in enumerate(attrs) if val[0] == 'href']
                if len(webs) > 0:
                    self.info['web'] = webs[0]

        elif self.mode == 'phone':
            if not 'phone' in self.info:
                # print('\nPhone:', attrs)
                phones = [val[1] for indx, val in enumerate(attrs) if val[0] == 'href']
                if len(phones) > 0:
                    if phones[0].lower().startswith('tel:'):
                        phones[0] = phones[0][len('tel:'):]
                    if len(phones[0]) > 0:
                        self.info['phone'] = phones[0].strip().replace('%20', '').replace(' ', '')


    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        self.mode == ''

    def handle_data(self, data):
        # print("Encountered some data  :", data)
        if data != '':
            # Set modes
            if data.startswith('Adresse'):
                # print('Adresse:', data[len('Adresse:'):].strip())
                if not 'adresse' in self.info:
                    if len(data) > len('Adresse: 1234'):
                        self.info['adresse'] = data[len('Adresse:'):].strip()
                    else:
                        self.mode = 'adresse'
            elif data.startswith('Telefon'):
                # print('Phone reached')
                if len(data) > len('Telefon:') + 5 and not 'phone' in self.info:
                    self.info['phone'] = data.strip().replace(' ', '').replace('Telefon:', '')
                else:
                    self.mode = 'phone'
                
            elif data.startswith('E-post') or data.startswith('Epost'):
                if len(data) > len('E-post:') + 5 and not 'email' in self.info:
                    self.info['email'] = data.strip().replace(' ', '').replace('E-post:', '')
                else:
                    self.mode = 'email'
            elif data.startswith('Nettsted') or data.startswith('Web') or data.startswith('Hjemmeside'):
                self.mode = 'web'

            # Set data
            elif self.mode == 'description':
                # print('new data:', data)
                if not 'description' in self.info:
                    if data.strip() != '':
                        self.info['description'] = data
                    self.mode == ''
            elif self.mode == 'adresse':
                if not 'adresse' in self.info:
                    self.info['adresse'] = data.strip()
            elif self.mode == 'phone':
                if not 'phone' in self.info:
                    self.info['phone'] = data.strip().replace(' ', '')
                    


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
    description
    adresse

image_fulltext (from images)
xreference (from metadata)
'''

eating_places = []

for data in json_file[2]['data']:
    if data['catid'] in ['39', '55'] and data['state'] == '1':

        # print('Starting on a new object!')

        eating_place = {}

        # title
        eating_place['title'] = data['title']

        # image_url
        eating_place['image_url'] = json.loads(data['images'])['image_fulltext']

        # position
        if eating_place['title'] == 'Fagn':
            eating_place['position'] = '10.396365 63.433984'
        else:
            pos = json.loads(data['metadata'])['xreference'].split(',')
            if len(pos) < 2:
                print(data)
                print(pos, eating_place['title'])

            eating_place['position'] = '%s %s' %(pos[1].strip(), pos[0].strip())

        # html_test = "<p>Michelinstjerne-belønnet restaurant på Lilleby, like nordøst for Trondheim sentrum. Her serveres ikke mat á la carte. I stedet bestemmer kjøkkenet hvilke smaker som skal rendyrkes, med utgangspunkt i råvarene som finnes på en gitt dag. Kokkene komponerer hver dag en unik kombinasjon av retter og vin. Man kan til vanlig velge mellom tre og fem retter. Credo var sammen med Fagn de to første restaurantene i Trondheim som mottok en Michelin-stjerne i februar 2019.<\/p>\r\n<h4>Kontaktinfo<\/h4>\r\n<p>Adresse: Ladeveien 9, Trondheim<\/p>\r\n<p>Telefon : <a href=\"tel:+47 954 37 028\">+47 954 37 028<\/a><\/p>\r\n<p>E-post: <a class=\"dark_gray partner-hover mailto\" href=\"mailto:credo@restaurantcredo.no\" rel=\"noindex, nofollow\">Send en e-post <\/a><\/p>\r\n<p>Nettsted: <a class=\"dark_gray url partner-hover\" href=\"http:\/\/www.restaurantcredo.no\" target=\"_blank\" rel=\"noindex, nofollow noopener noreferrer\">Besøk websiden <\/a><\/p>"
        html_test = data['introtext']
        
        html_test = html_test.replace('\r', '')
        html_test = html_test.replace('\n', '')
        html_test = html_test.replace('&quot;', '')
        # print(html_test)
        # html_test = html_test.replace('\\', '')
        # html_test = ''.join(html_test.split())

        parser = MyHTMLParser()
        parser.feed(html_test)

        # print('\n\n\n')
        # print(parser.info)

        for key, val in parser.info.items():
            # Adding the parsed info
            eating_place[key] = val

        all_keys = ['title', 'image_url', 'position', 'adresse',
                    'description', 'phone', 'email', 'web']

        for key in all_keys:
            if not key in eating_place:
                # print(key, 'not in eating_place. Adding empty')
                eating_place[key] = ''

        # Add default rating and price
        eating_place['rating'] = 3
        eating_place['price'] = 3

        if eating_place['title'] == 'Olivia Solsiden':
            print(html_test)



        eating_places.append(eating_place)

        # xreference = data['metadata'].keys() # .replace('\\','')
        # print(json.loads(data['metadata'])['xreference'].replace(',',' '))
        # break

with open('test.json', 'w') as outFile:
    # data = json.load(outFile)
    # for i in range(len(data)):
    #     if not data[i] == eating_places[i] and i == 0:
    #         print(data[i], eating_places[i])
    json.dump(eating_places, outFile, ensure_ascii=False, indent=4, sort_keys=True)