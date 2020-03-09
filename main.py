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

HOST            = "localhost"
URL             = "http://" + HOST + ":3000/api/dashboards/db"
API_KEY         = "eyJrIjoiOFpNbWpUcGRPY3p2eVpTT0Iza0F5VzdNU3hJcmZrSVIiLCJuIjoibXlLZXkyIiwiaWQiOjF9"
TIME_FROM       = "1998-04-03"
TIME_TO         = "2020-04-03"
HEAVY_HITTER_THRESHOLD = 0.2

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
    
    heavy_hitter_flag = 0
    for flow in switchMap[trigger_switch].ratios:
        ratio = switchMap[trigger_switch].ratios[flow]

        if ratio > HEAVY_HITTER_THRESHOLD:
            heavy_hitter_flag = 1
            if test_for_heavy_hitter(mysql_manager, flow, switchMap, flowMap, mapIp):
                print("Possible heavy hitter: " + mapIp[flow])

    if heavy_hitter_flag is 0:
        print("Possible synchronized incast, no heavy hitters found")
        

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

    

if __name__ == "__main__":
    main()