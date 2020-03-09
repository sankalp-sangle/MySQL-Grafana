import requests

from core import Dashboard_Properties
from core import Time
from core import Dashboard
from core import Panel
from core import Grid_Position
from core import Target
from core import MySQL_Manager
from core import Switch
from core import Flow
from core import QueryBuilder

HOST            = "localhost"
URL             = "http://" + HOST + ":3000/api/dashboards/db"
ANNOTATIONS_URL = "http://" + HOST + ":3000/api/annotations"
API_KEY         = "eyJrIjoiOFpNbWpUcGRPY3p2eVpTT0Iza0F5VzdNU3hJcmZrSVIiLCJuIjoibXlLZXkyIiwiaWQiOjF9"

HEAVY_HITTER_THRESHOLD = 0.2
YEAR_SEC = 31556926
UNIX_TIME_START_YEAR = 1970

DASHBOARD_TITLE = "Packet Capture Microburst HH 2"
VALUE_LIST = ['link_utilization','queue_depth']


headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + API_KEY
}

CLEANUP_QUERIES = ['set SQL_SAFE_UPDATES = 0', 'delete from packetrecords where time_in = 0']

def Int2IP(ipnum):
    o1 = int(ipnum / pow(2,24)) % 256
    o2 = int(ipnum / pow(2,16)) % 256
    o3 = int(ipnum / pow(2,8)) % 256
    o4 = int(ipnum) % 256
    return '%(o1)s.%(o2)s.%(o3)s.%(o4)s' % locals()

def main():
    
    mysql_manager = MySQL_Manager()

    for query in CLEANUP_QUERIES:
        mysql_manager.execute_query(query)
    
    mapIp = get_ip_addresses(mysql_manager)

    switchMap = initialize_switches(mysql_manager)
    flowMap = initialize_flows(mysql_manager)

    for switch in switchMap:
        switchMap[switch].populate_flow_list(mysql_manager)
        switchMap[switch].populate_ratios(mysql_manager)
        switchMap[switch].print_info(mapIp)
        

    for flow in flowMap:
        flowMap[flow].populate_switch_list(mysql_manager)
        flowMap[flow].populate_ratios(mysql_manager)
        flowMap[flow].print_info(mapIp)
        

    print(str(len(flowMap)) + " flows")
    print(str(len(switchMap)) + " switches") 
    print("\n")

    result = mysql_manager.execute_query('select switch from triggers')
    trigger_switch = result[1:][0][0]
    

    heavy_hitters = []

    heavy_hitter_flag = 0
    for flow in switchMap[trigger_switch].ratios:
        ratio = switchMap[trigger_switch].ratios[flow]

        if ratio > HEAVY_HITTER_THRESHOLD:
            heavy_hitter_flag = 1
            if test_for_heavy_hitter(mysql_manager, flow, switchMap, flowMap, mapIp):
                print("Possible heavy hitter: " + mapIp[flow])
                heavy_hitters.append(flow)

    print(heavy_hitters)

    if heavy_hitter_flag is 0:
        print("Possible synchronized incast, no heavy hitters found")



    #Dashboard creation

    #delete all existing annotations
    response = requests.request("GET", url=ANNOTATIONS_URL, headers=headers)
    annotations = response.json()
    for annotation in annotations:
        annotationId = annotation['id']
        response = requests.request("DELETE", url=ANNOTATIONS_URL + "/" + str(annotationId), headers=headers)

    #time_from and time_to are lists of a tuple, [(time in seconds, 0)] like so
    time_from_seconds = mysql_manager.execute_query('select min(time_in) from packetrecords')[1][0]
    time_to_seconds = mysql_manager.execute_query('select max(time_in) from packetrecords')[1][0]

    #Convert to date format
    year_from = UNIX_TIME_START_YEAR + (time_from_seconds // YEAR_SEC)
    year_to = UNIX_TIME_START_YEAR + 1 + (time_to_seconds // YEAR_SEC)
    
    assert year_from < year_to

    time_from = get_formatted_time(year_from)
    time_to = get_formatted_time(year_to)

    print(time_from, "\n", time_to)

    #create Panel list
    panelList = []

    #append Default Queries
    panelList.append(Panel(title="Default Panel: Link Utilization", targets = [Target(rawSql=QueryBuilder(value = 'link_utilization', metricList = ['switch', 'source_ip']).get_generic_query())]))
    panelList.append(Panel(title="Default Panel: Queue Depth", targets = [Target(rawSql=QueryBuilder(value = 'queue_depth', metricList = ['switch', 'source_ip']).get_generic_query())]))
    
    for flow in heavy_hitters:
        for value in VALUE_LIST:
            qb = QueryBuilder(value = value, metricList = ['switch', 'source_ip'], isConditional=True, conditionalClauseList=['source_ip = ' + str(flow)])
            panel = Panel(title=value +"(" + mapIp[flow] + ")", targets=[Target(rawSql=qb.get_generic_query())])
            # print(qb.get_generic_query())
            panelList.append(panel)

    dashboard = Dashboard(properties=Dashboard_Properties(title=DASHBOARD_TITLE ,time=Time(timeFrom=time_from, timeTo=time_to)), panels=panelList)
    
    payload = get_final_payload(dashboard)
    print("\nPayload:\n" + payload)
    response = requests.request("POST", url=URL, headers=headers, data = payload)
    json_response = str(response.text.encode('utf8'))
    print("\nResponse:\n" + json_response)
    
    dashboardId = response.json()['id']
    # print("Dashboard Id:" + str(dashboardId))

    #Post annotations

    trigger_time = mysql_manager.execute_query('select time_hit from triggers')[1][0]
    print(trigger_time)

    annotations_payload = "{ \"time\":" + str(trigger_time) + "000" + ", \"text\":\"Trigger Hit!\", \"dashboardId\":" + str(dashboardId) + "}"
    print("\nAnnotations Payload:\n" + annotations_payload)
    response = requests.request("POST", url=ANNOTATIONS_URL, headers=headers, data = annotations_payload)
    json_response = str(response.text.encode('utf8'))
    print("\nResponse:\n" + json_response)


def initialize_switches(mysql_manager):
    print("Initializing switches...")
    switchList = {}
    if mysql_manager is not None:
        result = mysql_manager.execute_query('select distinct switch from packetrecords')
        for row in result[1:]:
            switchList[row[0]] = Switch(identifier=row[0])
    
    return switchList

def initialize_flows(mysql_manager):
    print("Initializing flows...")
    flowList = {}
    if mysql_manager is not None:
        result = mysql_manager.execute_query('select distinct source_ip from packetrecords')
        for row in result[1:]:
            flowList[row[0]] = Flow(identifier=row[0])
    
    return flowList

def test_for_heavy_hitter(mysql_manager, flow, switchMap, flowMap, mapIp):
    print("Testing for flow:" + mapIp[flow])
    for switch in flowMap[flow].ratios:
        print("Switch:" + switch + " Ratio:" + str(flowMap[flow].ratios[switch]) )
        if flowMap[flow].ratios[switch] < HEAVY_HITTER_THRESHOLD:
            return False
    
    return True

def get_ip_addresses(mysql_manager):
    print("Generating IP map...")
    result = mysql_manager.execute_query('select distinct source_ip from packetrecords')
    mapIp = {}

    for row in result[1:]:
        for ip in row:
            mapIp[ip] = Int2IP(ip)
    return mapIp

def get_formatted_time(year):
    return "{}-{}-{}".format(year, "01", "01")

def get_final_payload(dashboard):
    payload = "{ \"dashboard\": {" + dashboard.get_json_string() + "}, \"overwrite\": true}"
    return payload
    

if __name__ == "__main__":
    main()