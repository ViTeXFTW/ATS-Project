# Setup and Run Instructions

> **Important**: Update the index and header variable in the top of main.py to match the topology used. Header flag is true if there is a header in the topology.csv file, index is either 0 or 1 depending on the indexing in topology.csv

## (Optional) Create Virtual Environment
If you don't have `venv` installed, run:
```plaintext
>$ pip install venv
```

Create a virtual environment:
```plaintext
>$ python3 -m venv .venv
```

Activate the virtual environment:
1. Navigate to `.venv/scripts/` (on Windows) or `.venv/bin/` (on macOS/Linux).
2. Activate the environment by running:
   - On Windows: `.\activate`
   - On macOS/Linux: `source activate`

## Install Requirements
Install the necessary packages:
```plaintext
>$ pip install -r requirements.txt
```

## Run the Script
To run the script, use the following command:
```plaintext
>$ python main.py
```

## Deactivate the Virtual Environment
Once you are done, you can deactivate the virtual environment by running:
```plaintext
>$ deactivate
```

## Input Files Requirements

The program expects two input CSV files in the `./input_files/` directory:
- `small-streams.v2.csv`
- `small-topology.v2.csv`

### Topology File Format
The topology file should contain rows in the following formats:
- Switch definition: `SW,<switch_name>,<number_of_ports>`
- End System definition: `ES,<system_name>,<number_of_ports>`
- Link definition: `LINK,<link_name>,<source_node>,<source_port>,<destination_node>,<destination_port>`

### Streams File Format
The streams file should contain columns for:
- StreamName
- SourceNode
- DestinationNode
- Size
- Period
- PCP (Priority Code Point)

## Output
The program will generate a solution file containing:
- StreamName
- MaxE2E(us)
- Deadline(us)
- Path
