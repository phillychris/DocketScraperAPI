
from requests import post
import json
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
    'Lawrence', 'Jefferson', 'Potter', 'Bedford', 'Mifflin', 'Elk', 'Pike']



for county in county_list:

    filename = 'references/court_offices_by_county/{}.json'.format(county.lower().replace(' ', '_'))

    if isfile(filename):
        print('JSON for {} already exists'.format(county))
        continue

    print('Checking: ', county)

    data = {'county': county}

    #print('data: ', json.dumps(data))

    headers = {'content-type': 'application/json'}

    #print('headers: ', headers)

    r = post(url, data=json.dumps(data), headers=headers)

    offices = json.loads(r.text)

    #del(offices['status'])

    #offices['county'] = county

    #print(offices); break;

    file = open(filename, 'w')
    file.write(json.dumps({'county': county, 'offices': offices['offices']}))
    file.close()

    #break
