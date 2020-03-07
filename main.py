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

def Int2IP(ipnum):
    o1 = int(ipnum / pow(2,24)) % 256
    o2 = int(ipnum / pow(2,16)) % 256
    o3 = int(ipnum / pow(2,8)) % 256
    o4 = int(ipnum) % 256
    return '%(o1)s.%(o2)s.%(o3)s.%(o4)s' % locals()

def main():
    
    mysql_manager = MySQL_Manager()
    mapIp = get_ip_addresses(mysql_manager)

    switchMap = initialize_switches(mysql_manager)
    flowMap = initialize_flows(mysql_manager)

    for switch in switchMap:
        switchMap[switch].populate_flow_list(mysql_manager)
        switchMap[switch].print_info(mapIp)
        # print("Switch " + switchMap[switch].identifier + '-> ' + str( [mapIp[x] for x in switchMap[switch].flowList] ) )
        # packetList = switchMap[switch].get_packet_count_from_switch(mysql_manager)
        # for row in packetList:
            # print( (mapIp[row[0]] if row[0] in mapIp else str(row[0]) ) + " - " + str(row[1]) )
        # print("\n")

    for flow in flowMap:
        flowMap[flow].populate_switch_list(mysql_manager)
        flowMap[flow].print_info(mapIp)
        # print("Flow " + mapIp[flowMap[flow].identifier] + '->' + str(flowMap[flow].switchList))

    print(str(len(flowMap)) + " flows")
    print(str(len(switchMap)) + " switches") 
    

     
    # answer = get_packet_count_from_trigger_switch_boundaries(mysql_manager)
    # total_pkts = sum([ i[1] for i in answer[1:] ])
    # print(total_pkts)

    # for row in answer[1:]:
    #     print( ( mapIp[row[0]] if row[0] in mapIp else str(row[0]) ) + " " + str(row[1] / total_pkts))

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




# def get_avg_link_util_from_trigger_switch_boundaries(mysql_manager):
#     HALF_WIDTH = 10000000 # 1 Micro

#     trigger_time = mysql_manager.execute_query('select time_hit from triggers')[1][0]
#     # print(str(trigger_time))
#     answer = mysql_manager.execute_query('select source_ip, count(hash) from packetrecords where switch in (select distinct switch from triggers) and time_in between ' + str(trigger_time - HALF_WIDTH) + ' and ' + str(trigger_time + HALF_WIDTH) + ' group by switch, source_ip')
#     return answer

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