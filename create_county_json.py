
from requests import post
import json
import csv
from os.path import isfile

url = 'http://localhost:8800/getCourtOffices/MDJ'

# From references/county_lookup.csv
county_list = ['Chester', 'Clarion', 'Berks', 'Blair', 'Clinton', 'Columbia', 'Crawford', 'Armstrong',
    'Beaver', 'Bradford', 'Clearfield', 'Cambria', 'Centre', 'Butler', 'Adams', 'Carbon', 'Cameron',
    'Lancaster', 'Northampton', 'Tioga', 'Allegheny', 'Erie', 'Bucks', 'Northumberland', 'Cumberland',
    'Westmoreland', 'Luzerne', 'Dauphin', 'Greene', 'Fayette', 'Somerset', 'Snyder', 'Union', 'York',
    'Huntingdon', 'Schuylkill', 'Wayne', 'Montour', 'Washington', 'Venango', 'Lycoming', 'Lehigh',
    'Delaware', 'Susquehanna', 'Mercer', 'Forest', 'Warren', 'Montgomery', 'Franklin', 'Fulton',
    'Indiana', 'Juniata', 'Perry', 'Monroe', 'Sullivan', 'Wyoming', 'Lackawanna', 'McKean', 'Lebanon',
    'Lawrence', 'Jefferson', 'Potter', 'Bedford', 'Mifflin', 'Elk', 'Pike', 'Philadelphia']

county_dict_list = []

priority_dict = {
    'Philadelphia': 1,
    'Bucks': 2,
    'Chester': 2,
    'Delaware': 2,
    'Montgomery': 2
}

finished_dict = {
    'Philadelphia': True,
    'Bucks': True,
    'Chester': True,
    'Delaware': True,
    'Montgomery': True
}
# Header row: common_pleas,county,magisterial
with open('references/county_lookup_cp.csv', newline='') as csvfile:
    counties = csv.DictReader(csvfile)
    for row in counties:
        county_dict_list.append(dict(row))
        #print(row)
        if row['county'] not in county_list:
            print('county_list missing:', row['county'])
        if len(row['common_pleas']) != 2 or len(row['magisterial']) != 2:
            print('Length error with: ', row['county'])

#print(county_dict_list)

for county_dict in county_dict_list:

    county_dict['priority'] = priority_dict[county_dict['county']] if county_dict['county'] in priority_dict else 3
    county_dict['backlog_2018_finished'] = finished_dict[county_dict['county']] if county_dict['county'] in finished_dict else False
    county_dict['backlog_2019_finished'] = finished_dict[county_dict['county']] if county_dict['county'] in finished_dict else False

#print(county_dict_list)

filename = 'references/county.json'
file = open(filename, 'w')
file.write(json.dumps({'counties': county_dict_list}, indent=4))
file.close()
