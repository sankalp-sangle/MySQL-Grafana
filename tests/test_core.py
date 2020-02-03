import unittest
import requests
import json
import datetime
import time

from core import Dashboard_Properties
from core import Time
from core import Dashboard
from core import Panel
from core import Grid_Position
from core import Target
from core import MySQL_Manager

URL             = "http://localhost:3000/api/dashboards/db"
API_KEY         = "eyJrIjoiOFpNbWpUcGRPY3p2eVpTT0Iza0F5VzdNU3hJcmZrSVIiLCJuIjoibXlLZXkyIiwiaWQiOjF9"
TIME_FROM = "2039-01-01"
TIME_TO   = "2042-01-01"

TEST_QUERY1 = r'SELECT time_in as \"time\", concat(\"Switch\",switch) AS metric, time_queue FROM packetrecords ORDER BY time_in'
TEST_QUERY2 = r'SELECT from_unixtime(time_in) as \"time\", concat(\"Switch\",switch) AS metric, time_queue FROM packetrecords ORDER BY time_in'

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

    def test_time_generation(self):

        YEAR_SEC = 31556926
        MONTH_SEC = 2629743
        DAY_SEC = 86400

        mysql_manager = MySQL_Manager()

        time_from = mysql_manager.execute_query('select min(time_in) from packetrecords')
        time_to = mysql_manager.execute_query('select max(time_in) from packetrecords')

        time_from_seconds = time_from[0][0]
        time_to_seconds = time_to[0][0]

        year_from = 1970 + time_from_seconds // YEAR_SEC
        year_to = 1970 + 1 + (time_to_seconds // YEAR_SEC)

        time_from = "{}-{}-{}".format( year_from, "01", "01")
        time_to = "{}-{}-{}".format(year_to, "01", "01")

        print(time_from, "\n", time_to)

        # time_from = time_from[0][0].strftime("%Y-%m-%d")
        # time_to = time_to[0][0].strftime("%Y-%m-%d")
        
        TEST_QUERY = ""
        if year_to < 2038:
            TEST_QUERY = TEST_QUERY2
        else:
            TEST_QUERY = TEST_QUERY1
        dashboard = Dashboard(properties=Dashboard_Properties(title="This is my test dashboard wuw" ,time=Time(timeFrom=time_from, timeTo=time_to)), panels=[Panel(title="My sample panel", targets = [Target(rawSql=TEST_QUERY)])])
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
        print(self.dashboard.get_json_string())

if __name__ == '__main__':
    unittest.main()

        
