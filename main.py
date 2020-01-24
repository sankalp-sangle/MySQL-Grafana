import requests
from core import Dashboard_Properties
from core import Dashboard

URL = "http://localhost:3000/api/dashboards/db"
API_KEY = 'eyJrIjoiR1NROFFyS215Sm9EeThIYkhDaVdmQlA2NFBTcjNXQ0IiLCJuIjoibXlLZXkiLCJpZCI6MX0='
headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + API_KEY
}


def main():

    properties = Dashboard_Properties()
    dashboard = Dashboard(panels = None,properties=properties)
    # print(dashboard.get_json_string())
    payload = "{ \"dashboard\": {" + dashboard.get_json_string() + "}, \"overwrite\": false}"
    # print(payload)
    
    response = requests.request("POST", url=URL, headers=headers, data = payload)
    print(response.text.encode('utf8'))



if __name__ == "__main__":
    main()