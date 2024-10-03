import csv
import networkx as nx

# Assumed default link speed in bits per second (e.g., 100 Mbps)
DEFAULT_LINK_SPEED = 1 * 10**6

def read_topology(filename):
    G = nx.Graph()
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            device_name = row['DeviceName']
            ports = row['Ports']
            # Assuming 'Ports' lists connected devices separated by semicolons
            connected_devices = [port.strip() for port in ports.split(';') if port.strip()]
            for connected_device in connected_devices:
                # Remove any port labels if present (e.g., "Port1=DeviceA" -> "DeviceA")
                if '=' in connected_device:
                    connected_device = connected_device.split('=')[1]
                G.add_edge(device_name, connected_device)
    return G

def read_streams(filename):
    streams = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stream = {
                'PCP': row['PCP'],
                'StreamName': row['StreamName'],
                'StreamType': row['StreamType'],
                'SourceNode': row['SourceNode'],
                'DestinationNode': row['DestinationNode'],
                'Size': int(row['Size']),  # in bytes
                'Period': row['Period'],
                'Deadline': row['Deadline']
            }
            streams.append(stream)
    return streams

def calculate_per_hop_delay(packet_size_bytes, link_speed_bps):
    # Transmission delay = packet size in bits / link speed in bits per second
    packet_size_bits = packet_size_bytes * 8
    transmission_delay = packet_size_bits / link_speed_bps
    # Assuming negligible queuing delay for simplicity
    queuing_delay = 0  # You can modify this based on your scheduling policy
    return transmission_delay + queuing_delay

def calculate_worst_case_delay(stream, G):
    source = stream['SourceNode']
    destination = stream['DestinationNode']
    packet_size = stream['Size']  # in bytes
    try:
        path = nx.shortest_path(G, source=source, target=destination)
    except nx.NetworkXNoPath:
        print(f"No path between {source} and {destination}")
        return None
    total_delay = 0
    for i in range(len(path) - 1):
        # For each link, calculate the per-hop delay
        per_hop_delay = calculate_per_hop_delay(packet_size, DEFAULT_LINK_SPEED)
        total_delay += per_hop_delay
    return total_delay

def main():
    topology_file = './src/data/example_topology.csv'
    streams_file = './src/data/example_streams.csv'
    G = read_topology(topology_file)
    streams = read_streams(streams_file)
    for stream in streams:
        worst_case_delay = calculate_worst_case_delay(stream, G)
        if worst_case_delay is not None:
            print(f"Stream {stream['StreamName']} worst-case delay: {worst_case_delay * 1000:.3f} ms, deadline: {int(stream['Deadline']) / 1000:.3f} ms")
        else:
            print(f"Could not calculate delay for stream {stream['StreamName']}")

if __name__ == "__main__":
    main()