'''
    - Code to assemble the different info files
    - Reads the logs from the INFO_DIR
    - Export INFO_DIR before this.
'''

import sys
import os

env_vars=os.environ
pwdir=os.getcwd()

info_dir=env_vars["INFO_DIR"]
os.chdir(info_dir)

node_fp=open("node_file.txt", "w")
comm_fp=open("comm_file.txt", "w")
sr_fp=open("sr_file.txt","w")               # a separate file to record the send receive calls
send_fp=open("send_file.txt","w")           # a separate file to record the send and isend calls

files=os.listdir()

fid=0

sr_calls=[]
send_calls=[]

rank=0
for fname in files:
    if fname.startswith("info-"):
        rank+=1
        fp=open(fname,"r")
        lines=fp.readlines()
        node_info=lines[0].split()
        node_info[-1]=node_info[-1].strip('\n')
        node_fp.write(f"{node_info[0]} {node_info[1]}\n")
        for i in range(1, len(lines)):
            line=lines[i].split()
            line[-1]=line[-1].strip('\n')
            if len(line)==5:    #normal MPI collective
                fid=max(fid, int(line[0]))
                comm_fp.write(f"{line[0]} {line[1]} {line[2]} {line[3]} {line[4]}\n")
            if len(line)==4:    #MPI_Sendrecv calls
                temp=f"{line[1]} {line[2]} {line[3]}"
                if len(sr_calls)==rank:
                    sr_calls[rank-1].append(temp)
                else:
                    sr_calls.append([temp])
            if len(line)==6:    #MPI_Send and MPI_Isend calls
                temp=f"{line[3]} {line[4]} {line[5]}"
                if len(send_calls)==rank:
                    send_calls[rank-1].append(temp)
                else:
                    send_calls.append([temp])

comm_fp.close()
node_fp.close()

for rank in sr_calls:
    for comm in rank:
        sr_fp.write(f"{comm}\n");
    sr_fp.write("*\n")

for rank in send_calls:
    for comm in rank:
        send_fp.write(f"{comm}\n")
    send_fp.write("*\n");

sr_fp.close()
send_fp.close()