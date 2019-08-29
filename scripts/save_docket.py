
import os
import json
from datetime import datetime
from time import sleep


curl_command = """curl '{}' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'  -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' –compressed -o {}"""

years = list(range(2019, 2000, -1))

for year in years:
    print('Starting {} at {}.'.format(year, datetime.now()))

    keep_going = True

    while keep_going:

        # Get files in directory
        files = os.listdir('meta')

        # Set keep_going to False, will be set to true if files are found
        keep_going = False

        for file in files:

            if file[-9:] == '{}.json'.format(year):

                with open('meta/{}'.format(file), 'r') as fp:
                    docket_dict = json.load(fp)

                #print(docket_dict)

                docket_pdf_path = 'docket/{}.pdf'.format(docket_dict['docket_number'])

                if not os.path.isfile(docket_pdf_path):

                    # We may have more files, keep going
                    keep_going = True

                    cc = curl_command.format(docket_dict['docket_sheet_url'], docket_pdf_path)

                    #print(cc)

                    os.system(cc)

                    #sleep(14.75)
                    sleep(8)
