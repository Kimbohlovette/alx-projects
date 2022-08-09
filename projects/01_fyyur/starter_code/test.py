from itertools import groupby

from app import *


rows = Venue.query.all()
print(rows)
venues_dict = {}

for row in rows:
  city_state = (row.city, row.state)
  if city_state not in venues_dict.keys():
    venues_dict[city_state] = []
  venues_dict[city_state].append(dict(
    id = row.id,
    name = row.name, 
    upcoming_shows = Show.query.filter(Show.venue_id == row.id, Show.start_date > datetime.today()).count()
  ))
  
data = [dict(city=k[0], state=k[1], venues=v) for k, v in venues_dict.items()]

for item in data:
  print('\n', item['city'])
  print(item['state'])
  for sub_item in item['venues']:
    print('\n',sub_item['id'])
    print(sub_item['name'])





