import numpy as np

DIRPATH = './src/data/'
STREAM_NAME = 'example_streams.csv'
TOPOLOGY_NAME = 'example_topology.csv'

stream_csv = np.loadtxt(DIRPATH + STREAM_NAME, delimiter=',', dtype=str)
topology_csv = np.loadtxt(DIRPATH + TOPOLOGY_NAME, delimiter=',', dtype=str)

print(stream_csv)
    
    