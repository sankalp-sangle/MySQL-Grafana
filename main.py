import requests
from core import Dashboard_Properties
from core import Time
from core import Dashboard

URL             = "http://localhost:3000/api/dashboards/db"
API_KEY         = "eyJrIjoiQjBXRFZ4NHJGVWsySWtneFp4VlVEbjVabm1NM0p6VnMiLCJuIjoibXlLZXkiLCJpZCI6MX0="
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
    dashboard = Dashboard(properties=properties)
    payload = get_final_payload(dashboard)
    # print(payload)
    send_dashboard_to_grafana(payload)

def send_dashboard_to_grafana(payload):
    response = requests.request("POST", url=URL, headers=headers, data = payload)
    print(response.text.encode('utf8'))

def get_final_payload(dashboard):
    payload = "{ \"dashboard\": {" + dashboard.get_json_string() + "}, \"overwrite\": false}"
    return payload

if __name__ == "__main__":
    main()