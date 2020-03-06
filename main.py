import requests

from core import Dashboard_Properties
from core import Time
from core import Dashboard
from core import Panel
from core import Grid_Position
from core import Target
from core import MySQL_Manager

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

    # print(mapIp)
     
    answer = get_packet_count_from_trigger_switch_boundaries(mysql_manager)
    total_pkts = sum([ i[1] for i in answer[1:] ])
    print(total_pkts)

    for row in answer[1:]:
        print( ( mapIp[row[0]] if row[0] in mapIp else str(row[0]) ) + " " + str(row[1] / total_pkts))

def get_packet_count_from_trigger_switch(mysql_manager):
    answer = mysql_manager.execute_query('select source_ip, count(hash) from packetrecords where switch in (select distinct switch from triggers) group by switch, source_ip')
    return answer
    
def get_packet_count_from_trigger_switch_boundaries(mysql_manager):
    HALF_WIDTH = 10000000 # 1 Micro

    trigger_time = mysql_manager.execute_query('select time_hit from triggers')[1][0]
    # print(str(trigger_time))
    answer = mysql_manager.execute_query('select source_ip, count(hash) from packetrecords where switch in (select distinct switch from triggers) and time_in between ' + str(trigger_time - HALF_WIDTH) + ' and ' + str(trigger_time + HALF_WIDTH) + ' group by switch, source_ip')
    return answer

def get_ip_addresses(mysql_manager):
    result = mysql_manager.execute_query('select distinct source_ip from packetrecords')
    mapIp = {}

    for row in result[1:]:
        for ip in row:
            mapIp[ip] = Int2IP(ip)
    return mapIp

    

if __name__ == "__main__":
    main()