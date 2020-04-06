import sys

import mysql.connector
import requests
from mysql.connector import Error

from core import (Dashboard, Dashboard_Properties, Datasource, Flow,
                  Grid_Position, MySQL_Manager, Panel, QueryBuilder, Switch,
                  Target, Time)

HOST            = "localhost"
URL             = "http://" + HOST + ":3000/api/dashboards/db"
ANNOTATIONS_URL = "http://" + HOST + ":3000/api/annotations"
DATASOURCE_URL  = "http://" + HOST + ":3000/api/datasources"
API_KEY         = "eyJrIjoia3J0T3JpcHl6U3d6Nzg0NU1zaFFhdE0zUW1CaVNSb04iLCJuIjoibXlrZXkiLCJpZCI6MX0="

YEAR_SEC = 31556926
UNIX_TIME_START_YEAR = 1970
MAX_WIDTH = 1000000 # Nanoseconds
LEFT_THRESHOLD = 0.3
RIGHT_THRESHOLD = 0.5

DASHBOARD_TITLE = str(sys.argv[1])
VALUE_LIST = ['link_utilization','queue_depth', 'control_plane']

flaggg = 0

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
    
    scenario = str(sys.argv[1])

    mysql_manager = MySQL_Manager(database=scenario)

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

    result = mysql_manager.execute_query('select switch from triggers')
    trigger_switch = result[1:][0][0]
    
    result_set = mysql_manager.execute_query('select max(queue_depth) from packetrecords')
    peakDepth = result_set[1][0]
    print("Peak Depth: " + str(peakDepth))

    result_set = mysql_manager.execute_query('select time_in, time_out, queue_depth from packetrecords where queue_depth = ' + str(peakDepth))
    peakTimeIn = result_set[1][0]
    peakTimeOut = result_set[1][1]
    print("\nTime of peak depth: " + str(peakTimeOut))

    #Find left and right
    result_set = mysql_manager.execute_query('select time_in, time_out, queue_depth from packetrecords where switch = \'' + trigger_switch + '\' order by time_out')
    # print(result_set)

    peakIndex = result_set.index( (peakTimeIn, peakTimeOut, peakDepth) )
    # print("Index -> " + str(peakIndex))

    lIndex = peakIndex - 1
    rIndex = peakIndex + 1

    while lIndex >= 0 and result_set[lIndex][2] > LEFT_THRESHOLD * peakDepth:
        lIndex = lIndex - 1

    while rIndex < len(result_set) and result_set[rIndex][2] > RIGHT_THRESHOLD * peakDepth:
        rIndex = rIndex + 1

    rIndex = (rIndex - 1) if rIndex == len(result_set) else rIndex
    lIndex = (lIndex + 1) if lIndex == 0 else lIndex

    # print(str(lIndex) + "|||" + str(rIndex))

    lTime = result_set[lIndex][0]
    rTime = result_set[rIndex][1]

    timeDiff = rTime - lTime

    print("\nLeft time: {} Right time: {} Time difference: {} microseconds".format(str(lTime), str(rTime), str(timeDiff/1000)))

    if timeDiff > MAX_WIDTH:
        print("\nCONCLUDE: Time Gap is of the order of milliseconds. Probably underprovisioned network.")
    else:
        result_set = mysql_manager.execute_query("select source_ip, count(hash) from packetrecords where switch = \'" + trigger_switch + "\' and time_in between " + str(lTime) + " and " + str(rTime) + " group by 1")
        
        data_points = []

        print("\nData points within the band:")
        for row in result_set[1:]:
            print("Flow:" + mapIp[row[0]] + " Count: " + str(row[1]))
            data_points.append(row[1])
        
        # Jain Fairness Index calculation
        # print(data_points)
        J_index = calculate_jain_index(data_points)

        n = len(data_points)
        print("\nTotal data points: " + str(sum(data_points)))
        
        print("\nJ Index : " + str(J_index)) 
        normalizedJIndex = (J_index - 1.0/n) / (1 - 1.0/n)
        print("Normalized J Index : " + str(normalizedJIndex))

        printConclusion(normalizedJIndex)        

    print("\n******************* END *******************\n")

    trigger_time = mysql_manager.execute_query('select time_hit from triggers')[1][0]

    for switch in switchMap:
        result_set = mysql_manager.execute_query("select min(time_in), max(time_out) from packetrecords where switch = '"+ switchMap[switch].identifier + "'")
        left_cutoff = result_set[1:][0][0]
        right_cutoff = result_set[1:][0][1]
        print("Calculating ratios for " + str(switchMap[switch].identifier))
        getRatioTimeSeries(mysql_manager, switchMap[switch].identifier, (left_cutoff + right_cutoff) // 2, scenario)

    data_source = Datasource(name=scenario, database_type="mysql", database=scenario, user="sankalp")
    json_body = "{ " + data_source.get_json_string() + " }"
    response = requests.request("POST", url=DATASOURCE_URL, headers=headers, data = json_body)
    # print(response.json())

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

    # print(time_from, "\n", time_to)

    #create Panel list
    panelList = []

    #append Default Queries
    panelList.append(Panel(gridPos=Grid_Position(x=0,y=0),title="Default Panel: Relative ratios of packets for each flow at Trigger Switch", targets = [Target(rawSql=QueryBuilder(time_column = "time_stamp", value= 'ratio', metricList = ['switch', 'source_ip'],  table='RATIOS').get_generic_query())], datasource=scenario))
    panelList.append(Panel(gridPos=Grid_Position(x=12,y=0),title="Default Panel: Link Utilization", targets = [Target(rawSql=QueryBuilder(value = 'link_utilization', metricList = ['switch']).get_generic_query())], datasource=scenario))
    panelList.append(Panel(gridPos=Grid_Position(x=0,y=11),title="Default Panel: Queue Depth", targets = [Target(rawSql=QueryBuilder(value = 'queue_depth * 80 / 1500', metricList = ['switch'], isConditional=True, conditionalClauseList=['switch = \'' + str(trigger_switch) + '\'']).get_generic_query())], datasource=scenario))
    panelList.append(Panel(gridPos=Grid_Position(x=12,y=11),title="Queue depth at peak at trigger switch", targets = [Target(rawSql=QueryBuilder(value = 'queue_depth * 80 / 1500', metricList = ['switch', 'source_ip'], isConditional=True, conditionalClauseList=['switch = \'' + str(trigger_switch) + '\'', 'time_in between ' + str(lTime) + ' AND ' + str(rTime)]).get_generic_query())], datasource=scenario, lines = False, points = True))
    panelList.append(Panel(gridPos=Grid_Position(x=0,y=22),title="Packet distribution at peak at trigger switch", targets = [Target(rawSql=QueryBuilder(value = 'source_ip % 10', metricList = ['source_ip'], isConditional=True, conditionalClauseList=['switch = \'' + str(trigger_switch) + '\'']).get_generic_query())], datasource=scenario, points = True, lines = False))    

    dashboard = Dashboard(properties=Dashboard_Properties(title=DASHBOARD_TITLE ,time=Time(timeFrom=time_from, timeTo=time_to)), panels=panelList)
    
    payload = get_final_payload(dashboard)
    # print("\nPayload:\n" + payload)
    response = requests.request("POST", url=URL, headers=headers, data = payload)
    json_response = str(response.text.encode('utf8'))
    # print("\nResponse:\n" + json_response)
    
    dashboardId = response.json()['id']
    # print("Dashboard Id:" + str(dashboardId))

    #Post annotations

    
    # print(trigger_time)

    annotations_payload = "{ \"time\":" + str(trigger_time) + "000" + ", \"text\":\"Trigger Hit!\", \"dashboardId\":" + str(dashboardId) + "}"
    # print("\nAnnotations Payload:\n" + annotations_payload)
    response = requests.request("POST", url=ANNOTATIONS_URL, headers=headers, data = annotations_payload)
    json_response = str(response.text.encode('utf8'))
    # print("\nResponse:\n" + json_response)

    annotations_payload = "{ \"time\":" + str(lTime) + "000" + ", \"text\":\"Left Width\", \"dashboardId\":" + str(dashboardId) + "}"
    # print("\nLeft Width Payload:\n" + annotations_payload)
    response = requests.request("POST", url=ANNOTATIONS_URL, headers=headers, data = annotations_payload)
    json_response = str(response.text.encode('utf8'))
    # print("\nResponse:\n" + json_response)

    annotations_payload = "{ \"time\":" + str(rTime) + "000" + ", \"text\":\"Right Width\", \"dashboardId\":" + str(dashboardId) + "}"
    # print("\nRight Width Payload:\n" + annotations_payload)
    response = requests.request("POST", url=ANNOTATIONS_URL, headers=headers, data = annotations_payload)
    json_response = str(response.text.encode('utf8'))


    

def printConclusion(normalizedJIndex):
    if normalizedJIndex > 0.7:
        print("\nCONCLUDE: It is probably a case of synchronized incast")
    elif normalizedJIndex < 0.45:
        print("\nCONCLUDE: It is probably a case of a dominant heavy hitter")
    else:
        print("\nCONCLUDE: Doesn't fall in either category")        

def calculate_jain_index(data_points):

    n = len(data_points)
    numerator = 0
    denominator = 0

    summation = sum(data_points)
    numerator = summation ** 2

    denominator = n *  sum( [x ** 2 for x in data_points] )

    J_index = numerator * 1.0 / denominator
    return J_index
    # print("\nResponse:\n" + json_response)




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

# def test_for_heavy_hitter(mysql_manager, flow, switchMap, flowMap, mapIp):
#     print("Testing for flow:" + mapIp[flow])
#     for switch in flowMap[flow].ratios:
#         print("Switch:" + switch + " Ratio:" + str(flowMap[flow].ratios[switch]) )
#         if flowMap[flow].ratios[switch] < HEAVY_HITTER_THRESHOLD:
#             return False
    
#     return True

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
    
def getRatioTimeSeries(mysql_manager, switch, time, scenario):
    INTERVAL = 100000
    result_set = mysql_manager.execute_query("select min(time_in), max(time_out) from packetrecords where switch = '"+ switch + "'")
    # print(result_set)
    left_cutoff = result_set[1:][0][0]
    right_cutoff = result_set[1:][0][1]

    INTERVAL = (right_cutoff - left_cutoff) // 125

    myDict = {}

    leftPointer = time
    while leftPointer > left_cutoff:
        result_set = mysql_manager.execute_query("select source_ip, count(hash) from packetrecords where time_in < " + str(leftPointer) + " AND time_out > " + str(leftPointer) + " and switch = '" + switch + "'" +  " GROUP BY source_ip")[1:]
        totalPackets = sum([row[1] for row in result_set])
        print("Total pkts at time " + str(leftPointer) + " is " + str(totalPackets))
        for row in result_set:
            if row[0] in myDict:
                myDict[row[0]].append( (leftPointer, 1.0 * row[1] / totalPackets) )
            else:
                myDict[row[0]] = []

        leftPointer = leftPointer - INTERVAL

    rightPointer = time + INTERVAL    
    while rightPointer < right_cutoff:
        result_set = mysql_manager.execute_query("select source_ip, count(hash) from packetrecords where time_in < " + str(rightPointer) + " AND time_out > " + str(rightPointer) +  " and switch = '" + switch + "'" +  " GROUP BY source_ip")[1:]
        totalPackets = sum([row[1] for row in result_set])
        print("Total pkts at time " + str(rightPointer) + " is " + str(totalPackets))
        for row in result_set:
            if row[0] in myDict:
                myDict[row[0]].append( (rightPointer, 1.0 * row[1] / totalPackets) )
            else:
                myDict[row[0]] = []

        rightPointer = rightPointer + INTERVAL
            
    
    # for ip in myDict:
    #     print(str(ip))
    #     for tuple in myDict[ip]:
    #         print(str(ip) + " " + str(tuple))

    insertIntoSQL(myDict, scenario, switch)

def insertIntoSQL(myDict, db_name, switch):
    global flaggg
    mysql_db = mysql.connector.connect(host="0.0.0.0", user="sankalp", passwd="sankalp")
    mycursor = mysql_db.cursor()
    mycursor.execute("use " + db_name)

    if flaggg == 0:
        mycursor.execute('DROP TABLE IF EXISTS RATIOS')
        flaggg = 1
        mycursor.execute('CREATE TABLE RATIOS (time_stamp bigint, source_ip bigint, switch VARCHAR(255), ratio decimal(5,3) )')

    for ip in myDict:
        query = 'INSERT INTO RATIOS (time_stamp, source_ip, switch, ratio) VALUES (%s, %s, %s, %s)'
        for (timestamp, ratio) in myDict[ip]:
            val = (timestamp, ip, switch, ratio)
            mycursor.execute(query, val)

    mysql_db.commit()




if __name__ == "__main__":
    main()
