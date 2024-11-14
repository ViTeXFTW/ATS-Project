import pandas as pd
import networkx as nx
import csv

# Paths for input files
streams_path = './input_files/small-streams.v2.csv'
topology_path = './input_files/small-topology.v2.csv'

# Load streams.csv file with explicit daelimiter and updated headers
streams_df = pd.read_csv(streams_path, header=0)

class Node:
    def __init__(self, typeNode, name, ports, queues):
        self.typeNode = typeNode
        self.name = name
        self.ports = ports
        self.queues = queues

class Stream:
    def __init__(self, name, size, rate):
        self.name = name
        self.size = size
        self.rate = rate


node_dict = {}

# Function to process the small-topology.csv file
def process_topology_file(filepath):
    switches = []
    links = []
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == 'SW':
                temp_dict = {}
                ports = int(row[2])
                for i in range(ports):
                    temp_dict[str(i)] = {}
                node_dict[row[1]] = Node(row[0], row[1], row[2], temp_dict)
            elif row[0] == 'ES':
                node_dict[row[1]] = Node(row[0], row[1], row[2], {'1': {}})
            elif row[0] == 'LINK':
                links.append(row)
    return switches, links


# Process the topology file
switches, links = process_topology_file(topology_path)


# Build the network graph from links
def build_graph(links):
    G = nx.Graph()
    for link in links:
        _, link_name, src_node, src_port, dst_node, dst_port = link[:6]
        default_bandwidth = 1e9  # Assuming 1 Gbps default bandwidth
        # Add an edge with additional attributes for link name, bandwidth, and ports
        G.add_edge(
            src_node,
            dst_node,
            link_name=link_name,
            bandwidth=default_bandwidth,
            src_port={src_node: src_port, dst_node: dst_port}
        )
    return G


# Build the graph based on links
G = build_graph(links)

# Calculate shortest paths for all streams
def new_calculate_shortest_paths(G, streams_df):
    paths = {}
    outputPaths = {}
    for _, stream in streams_df.iterrows():
        source = stream['SourceNode']
        destination = stream['DestinationNode']
        # Calculate the shortest path
        path = nx.shortest_path(G, source=source, target=destination)

        # Collect the path details with ports used for each hop
        path_with_ports = []
        for i in range(len(path) - 2):
            i += 1
            src_node = path[i-1]
            cur_node = path[i]
            dst_node = path[i + 1]
            # Get the edge data to find which ports are used
            edge_data1 = G[src_node][cur_node]
            edge_data2 = G[cur_node][dst_node]
            src_port = edge_data1['src_port'][src_node]
            cur_dst_port = edge_data1['src_port'][cur_node]
            cur_src_port = edge_data2['src_port'][cur_node]
            dst_port = edge_data2['src_port'][dst_node]
            path_with_ports.append({
                'from_node': src_node,
                'src_port': src_port,
                'cur_node': cur_node,
                'cur_dst_port': cur_dst_port,
                'cur_src_port': cur_src_port,
                'to_node': dst_node,
                'dst_port': dst_port
            })
        print(stream['StreamName'], " ", path_with_ports)
        # Store the path with port details for this stream
        paths[stream['StreamName']] = path_with_ports
    return paths

new_shortest_paths = new_calculate_shortest_paths(G, streams_df)


# Calculate shortest paths for all streams
def calculate_shortest_paths(G, streams_df):
    paths = {}
    outputPaths = {}
    for _, stream in streams_df.iterrows():
        source = stream['SourceNode']
        destination = stream['DestinationNode']
        # Calculate the shortest path
        path = nx.shortest_path(G, source=source, target=destination)

        # Collect the path details with ports used for each hop
        path_with_ports = []
        for i in range(len(path) - 1):
            src_node = path[i]
            dst_node = path[i + 1]
            # Get the edge data to find which ports are used
            edge_data = G[src_node][dst_node]
            link_data = edge_data['link_name']
            src_port = edge_data['src_port'][src_node]
            dst_port = edge_data['src_port'][dst_node]
            path_with_ports.append({
                'from_node': src_node,
                'src_port': src_port,
                'to_node': dst_node,
                'dst_port': dst_port,
                'link': link_data
            })

        # Store the path with port details for this stream
        paths[stream['StreamName']] = path_with_ports
    return paths


# Calculate the shortest paths for each stream
shortest_paths = calculate_shortest_paths(G, streams_df)


# Calculate leaky bucket parameters (r = size/period)
def calculate_leaky_bucket(streams_df):
    streams_df['Size'] = streams_df['Size'] * 8
    streams_df['Rate (r)'] = streams_df['Size'] / (streams_df['Period'] / 1e6)  # Convert period to seconds
    return streams_df


# Apply leaky bucket calculation
streams_df = calculate_leaky_bucket(streams_df)


def PopuQueues():
    for stream_id, path in new_shortest_paths.items():
        pcp = streams_df[streams_df['StreamName'] == stream_id]['PCP'].values[0]
        size = streams_df[streams_df['StreamName'] == stream_id]['Size'].values[0]
        rate = streams_df[streams_df['StreamName'] == stream_id]['Rate (r)'].values[0]
        for item in path:
            node = node_dict.get(item['from_node'])
            if node is not None and node.typeNode == "ES":
                port = item['src_port']
                if node.queues[port].get(pcp) is not None:
                    node.queues[port][pcp].append(Stream(stream_id, size, rate))
                else:
                    node.queues[port][pcp] = [Stream(stream_id, size, rate)]
            node = node_dict.get(item['cur_node'])
            outport = item['cur_src_port']
            inport = item['cur_dst_port']
            if node.queues[outport].get(pcp) is None:
                node.queues[outport][pcp] = {inport: [Stream(stream_id, size, rate)]}
            elif node.queues[outport][pcp].get(inport) is not None:
                node.queues[outport][pcp][inport].append(Stream(stream_id, size, rate))
            else:
                node.queues[outport][pcp][inport] = [Stream(stream_id, size, rate)]

    #for key, node in node_dict.items():
       #print("key: ", key, " node: ", node.queues)












PopuQueues()


def getMAX2E():
    for s_id, path in new_shortest_paths.items():
        pcp = streams_df[streams_df['StreamName'] == s_id]['PCP'].values[0]
        size = streams_df[streams_df['StreamName'] == s_id]['Size'].values[0]
        rate = streams_df[streams_df['StreamName'] == s_id]['Rate (r)'].values[0]
        delay = 0
        r = 1e9
        for item in path:
            bH = 0
            bC = 0
            rH = 0
            L = 0
            node = node_dict.get(item['from_node'])
            if node is not None and node.typeNode == "ES":
                port = item['src_port']
                portQueues = node.queues[port]
                for priority, list in portQueues.items():
                    if priority > pcp:
                        for stream in list:
                            bH += stream.size
                            rH += stream.rate
                    elif priority == pcp:
                        for stream in list:
                            if stream.name != s_id:
                                bC += stream.size
                    else:
                        for stream in list:
                            if stream.size > L:
                                L = stream.size
                delay += (bH + bC + L) / (r - rH) + size / r
                print(s_id, " ", ( (bH + bC + L) / (r - rH) + size / r) * 1e6)
                bH = 0
                bC = 0
                rH = 0
                L = 0

            node = node_dict.get(item['cur_node'])
            outport = item['cur_src_port']
            inport = item['cur_dst_port']
            portQueues = node.queues[outport]
            for priority, pairs in portQueues.items():
                for port, list in pairs.items():
                    if priority > pcp:
                        for stream in list:
                            bH += stream.size
                            rH += stream.rate
                    elif priority == pcp:
                        for stream in list:
                            if stream.name != s_id:
                                bC += stream.size
                    else:
                        for stream in list:
                            if stream.size > L:
                                L = stream.size
            delay += (bH + bC + L) / (r - rH) + size / r
            print(s_id, " ", ( (bH + bC + L) / (r - rH) + size / r) * 1e6)

        delay *= 1e6
        print("Stream: ", s_id, " delay: ", delay)

getMAX2E()

def getATSWorstCaseDelay(stream_id):
    # Get the priority for the given stream
    priority = streams_df[streams_df['StreamName'] == stream_id]['PCP'].values[0]
    # Get the path information for the stream
    spath = shortest_paths[stream_id]

    delay = 0
    r = 1e9
    for node in spath:
        bH = 0
        bC = 0
        lL = 0
        rH = 0
        for s_id, path in shortest_paths.items():
            if s_id == stream_id:
                continue

            pcp = streams_df[streams_df['StreamName'] == s_id]['PCP'].values[0]
            size = streams_df[streams_df['StreamName'] == s_id]['Size'].values[0]
            rate = streams_df[streams_df['StreamName'] == s_id]['Rate (r)'].values[0]

            if node in path:
                if pcp > priority:
                    bH += size
                    rH += rate
                elif pcp == priority:
                    bC += size
                elif pcp < priority:
                    if size > lL:
                        lL = size
        delay += (bH + bC + lL) / (r - rH) + size / r
    delay *= 1e6
    return delay


# Display the streams data with calculated rates (leaky bucket)
print("Streams Data with Leaky Bucket Rates:")
print(streams_df.head())  # Print the first few rows of the streams dataframe

# Display shortest paths, transmission times, and deadlines
print("\nShortest paths, transmission times, deadlines, and maxE2E for each stream:")
for stream_id, path in shortest_paths.items():
    # Extract deadline for each stream
    filtered_df = streams_df[streams_df['StreamName'].str.strip() == stream_id.strip()]
    if not filtered_df.empty:
        deadline = filtered_df['Deadline'].values[0]
    else:
        print(f"Warning: Stream ID {stream_id} not found in dataframe!")
        deadline = "N/A"

    # Calculate transmission time in microseconds


    # In this case, maxE2E is based on the transmission time, but you could include other logic here to calculate WCD
    max_e2e = getATSWorstCaseDelay(stream_id)  # This can be adjusted as needed if the calculation differs

    # Display the results
    print(
        f"{stream_id}: Path: {path}, Deadline: {deadline} us, maxE2E: {max_e2e:.6f} us, rate: {streams_df[streams_df['StreamName'] == stream_id]['Rate (r)'].values[0]} bps")

    # Check if the flow meets its deadline
    if max_e2e <= deadline:
        print(f"  Status: Flow meets the deadline!")
    else:
        print(f"  Status: Flow exceeds the deadline.")
