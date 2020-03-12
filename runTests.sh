# runTests.sh will be stored in MySQL-Grafana folder

#Configure: Path to DejaVu repository stored in dejavuPath
#Configure: Path to MySQL-Grafana repository stored in mysqlGrafanaPath
dejavuPath="/Users/sankalpsangle/Desktop/DejaVu"
mysqlGrafanaPath="/Users/sankalpsangle/Desktop/MySQL-Grafana"

rm $mysqlGrafanaPath/results2.txt

pathToRecords="/dejavu-replay/results/collection_trace/microburst_incast_sync"

cd $dejavuPath/dejavu-replay

for i in 1 2 3 4 5
do
    python $dejavuPath/dejavu-replay/netplay.py $dejavuPath$pathToRecords$i.pcap
    echo "Loaded SQL records "$pathToRecords$i.pcap
    python3 $mysqlGrafanaPath/main.py >> $mysqlGrafanaPath/results2.txt
done

pathToRecords="/dejavu-replay/results/collection_trace/microburst_incast_heavyhitter"

for i in 1 2 3 4 5
do
    python $dejavuPath/dejavu-replay/netplay.py $dejavuPath$pathToRecords$i.pcap
    echo "Loaded SQL records "$pathToRecords$i.pcap
    python3 $mysqlGrafanaPath/main.py >> $mysqlGrafanaPath/results2.txt
done
