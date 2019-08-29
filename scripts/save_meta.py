
import os
import requests
import json
from datetime import datetime
from time import sleep

"""
curl --header "Content-Type: application/json"     --request POST     --data '{"docket_numbers": ["MC-51-CR-0039201-2018", "CP-51-CR-0007725-2018", "CP-09-CR-0006227-2018", "CP-15-CR-0003691-2018", "CP-23-CR-0006272-2018"]}'     http://3.91.149.8:8800/lookupMultipleCPDocketsEfficiently

SELECT substring(docket_num, 1, 8), YEAR(date_filed), COUNT(*)
FROM arrests
WHERE substring(docket_num, 1, 2) != 'MJ'
    AND county = 'Philadelphia'
GROUP BY substring(docket_num, 1, 8), YEAR(date_filed)
ORDER BY substring(docket_num, 1, 8), YEAR(date_filed);
"""

#url = 'http://3.91.149.8:8800/lookupMultipleCPDocketsEfficiently'
url = 'http://localhost:8800/lookupMultipleCPDocketsEfficiently'
#url = 'http://10.200.22.8:8800/lookupMultipleCPDocketsEfficiently'


headers = {'content-type': 'application/json'}

break_at_num_missing_in_row = 25

#years = list(range(2019, 2017, -1))
years = [2018]

court_type = 'CP'#or MC for Philly

county_number = '51'# Philadelphia
#county_number = '09'# Bucks

docket_type = 'CR'

num_per_request = 3

def return_docket_number(court_type, county_number, docket_type, i, year):
    docket_i = str(i).zfill(7)
    return '{}-{}-{}-{}-{}'.format(court_type, county_number, docket_type, docket_i, year)

for year in years:
    print('Starting {} at {}.'.format(year, datetime.now()))

    num_missing_in_row = 0

    current_index = 0

    not_found_flag = False

    while not not_found_flag:
        current_index += 1

        docket = return_docket_number(court_type, county_number, docket_type, current_index, year)

        #print('meta/{}.json'.format(docket), '  ', 'error/{}.json'.format(docket))

        not_found_flag = not os.path.isfile('meta/{}.json'.format(docket)) and not os.path.isfile('error/{}.json'.format(docket))

    print('Starting at {} for year {}'.format(current_index, year))

    while num_missing_in_row < break_at_num_missing_in_row:

        current_index_in_case_of_error = current_index

        try:

            docket_numbers = []

            for i in list(range(current_index, current_index + num_per_request)):

                #docket_i = str(i).zfill(7)

                #docket = '{}-{}-{}-{}-{}'.format(court_type, county_number, docket_type, docket_i, year)

                docket = return_docket_number(court_type, county_number, docket_type, i, year)

                docket_numbers.append(docket)

            current_index += num_per_request

            data = {'docket_numbers': docket_numbers}


            r = requests.post(url, data=json.dumps(data), headers=headers)

            #print('r.text:', r.text)

            response_dict = json.loads(r.text)

            for docket in response_dict['dockets']:

                d = response_dict['dockets'][docket]
                #print('d:', d)
                d['created_at'] = str(datetime.now())

                if 'error' in response_dict['dockets'][docket]:
                    print(response_dict['dockets'][docket]['error'])

                    #if response_dict['dockets'][docket]['error'] == 'No Dockets Found for: {}'.format(docket):
                    #    num_missing_in_row += 1
                    # Do this for any error
                    num_missing_in_row += 1

                    filename = 'error/{}.json'.format(docket)

                else:

                    num_missing_in_row = 0

                    filename = 'meta/{}.json'.format(docket)

                with open(filename, 'w') as f:
                    f.write(json.dumps(d))

        except Exception as e:

            num_missing_in_row += 1

            print('Received Error:', e)
            print('Waiting {} minute(s)'.format(num_missing_in_row))

            sleep(num_missing_in_row * 60)

            current_index = current_index_in_case_of_error


        sleep(54)






#docket_numbers = ["MC-51-CR-0039201-2018", "CP-51-CR-0007725-2018", "CP-09-CR-0006227-2018", "CP-15-CR-0003691-2018", "CP-23-CR-0006272-2018"]
