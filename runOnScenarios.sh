for i in 1 2 3 4 5
do
    echo "Testing Scenario :"microburst_incast_sync$i > results/microburst_incast_sync$i.txt
    python3 main.py microburst_incast_sync$i >> results/microburst_incast_sync$i.txt
    echo "Testing Scenario :"microburst_incast_heavyhitter$i > results/microburst_incast_heavyhitter$i.txt
    python3 main.py microburst_incast_heavyhitter$i >> results/microburst_incast_heavyhitter$i.txt
done

grep -E 'Normalized|CONCLUDE' results/* > results/summary.txt