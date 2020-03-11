cd  ~/DejaVu/myenv
source bin/activate
cd ../dejavu-replay

path="./results/collection_trace/microburst_incast_heavyhitter"

for i in 1 2 3 4 5
do
    python netplay.py $path$i.pcap
done