import unittest
import requests

from core import Dashboard_Properties
from core import Time
from core import Dashboard
from core import Panel
from core import Grid_Position

URL             = "http://localhost:3000/api/dashboards/db"
API_KEY         = "eyJrIjoiOFpNbWpUcGRPY3p2eVpTT0Iza0F5VzdNU3hJcmZrSVIiLCJuIjoibXlLZXkyIiwiaWQiOjF9"

headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + API_KEY
}

def get_final_payload(dashboard):
    payload = "{ \"dashboard\": {" + dashboard.get_json_string() + "}, \"overwrite\": true}"
    return payload

class Test_Core(unittest.TestCase):

    def test_dashboard(self):

        dashboard = Dashboard()
        payload = get_final_payload(dashboard)
        response = requests.request("POST", url=URL, headers=headers, data = payload)
        json_response = str(response.text.encode('utf8'))
        self.assertTrue("success" in json_response)

if __name__ == '__main__':
    unittest.main()

        
