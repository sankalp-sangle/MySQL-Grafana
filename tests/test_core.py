import unittest
import requests
import json

from core import Dashboard_Properties
from core import Time
from core import Dashboard
from core import Panel
from core import Grid_Position
from core import Target

URL             = "http://172.26.191.138:3000/api/dashboards/db"
API_KEY         = "eyJrIjoia3J0T3JpcHl6U3d6Nzg0NU1zaFFhdE0zUW1CaVNSb04iLCJuIjoibXlrZXkiLCJpZCI6MX0="
TIME_FROM = "2039-01-01"
TIME_TO   = "2042-01-01"

TEST_QUERY = r'SELECT time_in DIV 86400 * 86400 as \"time\", switch AS metric, avg(drops) FROM packetrecords group by 1,2 ORDER BY time_in DIV 86400 * 86400'

headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + API_KEY
}

# function to check if a json string is valid

def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True

def get_final_payload(dashboard):
    payload = "{ \"dashboard\": {" + dashboard.get_json_string() + "}, \"overwrite\": true}"
    return payload

class Test_Core(unittest.TestCase):

    def setUp(self):
        self.time = Time(timeFrom=TIME_FROM, timeTo=TIME_TO)
        self.targets = [Target(format = Target.DEFAULT_FORMAT, rawQuery = True, rawSql = Target.DEFAULT_RAW_SQL, refId = Target.DEFAULT_REFID)]
        self.gridPos = Grid_Position()
        self.panels = [Panel(targets = self.targets, gridPos = self.gridPos)]    
        self.properties = Dashboard_Properties(time = self.time)
        self.dashboard = Dashboard(panels = self.panels, properties = self.properties)

    def tearDown(self):
        pass

    def test_dashboard(self):

        dashboard = Dashboard(properties=Dashboard_Properties(title="Test Dashboard" ,time=Time(timeFrom="2039-10-01", timeTo="2042-01-01")), panels=[Panel(title="My sample panel", targets = [Target(rawSql=TEST_QUERY)])])
        payload = get_final_payload(dashboard)
        print(payload)
        response = requests.request("POST", url=URL, headers=headers, data = payload)
        json_response = str(response.text.encode('utf8'))
        print(json_response)
        self.assertTrue("success" in json_response)

    def test_get_json_string(self):
        self.assertTrue(is_json("{" + self.time.get_json_string() + "}"))
        for target in self.targets:
            self.assertTrue(is_json("{" + target.get_json_string() + "}"))
        self.assertTrue(is_json("{" + self.gridPos.get_json_string() + "}"))
        for panel in self.panels:
            self.assertTrue(is_json("{" + panel.get_json_string() + "}"))

if __name__ == '__main__':
    unittest.main()

        
