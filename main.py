import requests
from core import Dashboard_Properties
from core import Time
from core import Dashboard
from core import Panel
from core import Grid_Position

URL             = "http://localhost:3000/api/dashboards/db"
API_KEY         = "eyJrIjoiOFpNbWpUcGRPY3p2eVpTT0Iza0F5VzdNU3hJcmZrSVIiLCJuIjoibXlLZXkyIiwiaWQiOjF9"
TIME_FROM       = "1998-04-03"
TIME_TO         = "2020-04-03"
DASHBOARD_TITLE = "This is a sample title!"

headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + API_KEY
}


def main():
    time = Time(timeFrom=TIME_FROM, timeTo=TIME_TO)
    properties = Dashboard_Properties(title=DASHBOARD_TITLE, time=time)
    
    panels = []
    panels.append(Panel(title="Panel Number 1"))
    panels.append(Panel(title="Panel Number 2"))
    panels.append(Panel(title="Panel Number 3"))
    
    dashboard = Dashboard(properties=properties, panels=panels)
    payload = get_final_payload(dashboard)
    # print(payload)
    send_dashboard_to_grafana(payload)

def send_dashboard_to_grafana(payload):
    response = requests.request("POST", url=URL, headers=headers, data = payload)
    print(response.text.encode('utf8'))

def get_final_payload(dashboard):
    payload = "{ \"dashboard\": {" + dashboard.get_json_string() + "}, \"overwrite\": true}"
    return payload

if __name__ == "__main__":
    main()