# IPMPI communication model

This directory contains the modified IPMPI code, and python scripts for communication model.

## IPMPI code

- To compile the ipmpi code, go into the ipmpi directory and follow the readme instructions present there.
- Need to load gnu8/8.3.0 module in PARAM to compile the IPMPI.
- After compiling the ipmpi, need to source the ipmpi binary to use the profiler.
- export "INFO_DIR" before using the IPMPI, it is the location where all IPMPI logs are stored.

## Flow of communication model

- IPMPI profiler generates the log files for each rank, which contains the information about the communications.
- assemble.py generates 4 files - comm_file.txt, node_file.txt, sr_file.txt, send_file.txt
- "comm_file.txt" stores the communication steps for all the MPI collective functions.
- "send_file.txt" stores the MPI_Send() and MPI_Isend() calls.
- "sr_file.txt" stores the MPI_Sendrecv() calls.
- "node_file.txt" stores the rank to node mapping for each rank.
- These 4 files, will be utilized by the "comm_model.py".

- comm model uses the OSU benchmark for latency and bandwith benchmarking between nodes.
- Also we need to export environment variables "LBDIR", "IPMPI_RUNS_DIR"


```sh
$ source setup.sh
$ python3 assemble.py
$ python3 comm_model.py $arguments$
```