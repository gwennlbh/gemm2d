run:
    make || exit 0
    smpirun -np 4 -hostfile hostfiles/cluster_hostfile.txt -platform platforms/cluster_crossbar.xml  --algorithm p2p --niter 2 -c -v
