import json
import logging
from datetime import datetime
from bs4 import BeautifulSoup as soup

import requests
from waste_collection_schedule import Collection   

TITLE = "North Somerset.gov.uk"
DESCRIPTION = "Source for n-somerset.gov.uk services for North Somerset, UK."
URL = "n-somerset.gov.uk"

TEST_CASES = {
    "Walliscote Grove Road, Weston super Mare": {
        "uprn": "24009468",
        "postcode": "BS23 1UJ"
    } ,
    "Walliscote Road, Weston super Mare": {
        "uprn": "24136727",
        "postcode": "BS23 1EF"
    },
}

ICONS = {
    "RUBBISH": "mdi:trash-can",
    "RECYCLING": "mdi:recycle",
    "FOOD": "mdi:food",
} 

_LOGGER = logging.getLogger(__name__)

class Source:
    def __init__(self, uprn, postcode):
        self._uprn = uprn
        self._postcode = postcode

    def fetch(self):
        request = requests.post("https://forms.n-somerset.gov.uk/Waste/CollectionSchedule", 
            data = {
                "PreviousHouse": '', 
                "PreviousPostcode": '-', 
                "Postcode": self._postcode, 
                "SelectedUprn": self._uprn 
            }
        )  

        soup_result = soup(request.text, 'html.parser').table

        entries = []

        fields = []
        table_data = []

        for tr in soup_result.find_all('tr'):
            for th in tr.find_all('th'): 
                fields.append(th.text)

        for tr in soup_result.find_all('tr'):
            datum = {}
            for i, td in enumerate(tr.find_all('td')):
                datum[fields[i]] = td.text 
            if datum:
                table_data.append(datum)

        if not table_data: 
            return entries

        for collection in table_data:
            try: 
                entries.append(
                    Collection(
                        date = datetime.strptime(collection["Next collection date"], "%A %d %B").replace(year=datetime.now().year).date(),
                        t = collection["Service"],
                        icon = ICONS[collection["Service"].upper()],
                    )
                )
            except ValueError:
                pass   

        return entries
