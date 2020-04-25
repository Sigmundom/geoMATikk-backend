import json

with open('ratingprice.json', 'r') as j:
    restauranter = json.load(j)

kitchen_data = open('tags_restauranter.txt', 'r')

i = 0

for line in kitchen_data:
    i += 1
    if i > 8:
        parts = line.strip('\n').split(' : ')
        found = False
        # print(i)
        for r_i in range(len(restauranter)):
            if restauranter[r_i]['title'] == parts[0]:
                kitchens = parts[1].split(' ; ')[1].replace(' ', '').split(',')
                # print(kitchens)
                restauranter[r_i]['kitchen'] = kitchens


for r in restauranter:
    try:
        print(r['kitchen'])
    except Exception as e:
        print(r['title'])
        r['kitchen'] = []

with open('done.json', 'w') as outFile:
    json.dump(restauranter, outFile, ensure_ascii=False, indent=4, sort_keys=True)
