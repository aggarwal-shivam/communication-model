'''
    - This code uses the files generated by assmeble.py
    - Set the environment variables that are being used in the code.
    - Need to give arguments related to the app configuration.
    - Final file will be written at the IPMPI_RUNS_DIR
'''


import sys
import os
import subprocess as sp 

app=sys.argv[1]
nodes=sys.argv[2]
ppn=sys.argv[3]
nx=sys.argv[4]
ny=sys.argv[5]
nz=sys.argv[6]
it=sys.argv[7]

env_vars=os.environ
info_dir=env_vars["INFO_DIR"]

os.chdir(info_dir)

node_fp=open("node_file.txt","r")
comm_fp=open("comm_file.txt","r")
sr_file=open("sr_file.txt","r")
send_file=open("send_file.txt","r")

same_node_latency={
    0 : 2.01,
    1 : 1.76,
    2 : 1.45,
    4 : 1.55,
    8 : 1.32,
    16 : 1.32,
    32 : 1.74,
    64 : 1.36,
    128 : 1.39,
    256 : 1.42,
    512 : 1.46,
    1024 : 1.64,
    2048 : 2.61,
    4096 : 2.30,
    8192 : 3.01,
    16384 : 4.31,
    32768 : 6.74,
    65536 : 6.32,
    131072 : 9.55,
    262144 : 16.41,
    524288 : 36.38,
    1048576 : 98.82,
    2097152 : 235.21,
    4194304 : 476.69
}

same_node_bw={
    1 : 0.59,
    2 : 1.18,
    4 : 2.16,
    8 : 5.19,
    16 : 7.34,
    32 : 0.36,
    64 : 40.39,
    128 : 79.67,
    256 : 158.36,
    512 : 175.30,
    1024 : 622.26,
    2048 : 1202.02,
    4096 : 2135.31,
    8192 : 3815.50,
    16384 : 5420.32,
    32768 : 6932.61,
    65536 : 14125.16,
    131072 : 16539.06,
    262144 : 17850.12,
    524288 : 16665.97,
    1048576 : 12041.68,
    2097152 : 9107.28,
    4194304 : 9021.23,
}

rank_to_node={}
latency_dict={} #We will make the whole values in a dict: latency_dict: { 'csews1_to_csews2': {"msg_size1": "l1", "msg_size2": "l2"}  }
bw_dict={}  #similar structure to latency will be used by the bandwidth
node_list=[]

#storing the mapping between rank to node in a dict
node_lines=node_fp.readlines()

for line in node_lines:         #getting all the nodes used by the application
    line=line.split(" ")
    key=int(line[0])
    # val=line[1].strip('\n')
    val=line[1]
    val=val.rstrip(".iitk.ac.in\n")
    rank_to_node[key]=val
    node_list.append(val)

node_list=sorted(list(set(node_list)))

# print("The nodes used: ")
# print(node_list)
# print()

#print(node_list)
# print(f"rank to node_mapping: \n")
# for k,v in rank_to_node.items():
#     print(f"{k} : {v}")
# print()

#Now we need to get the latency and bandwidth info for these nodes 
for p in range(len(node_list)-1):
    for q in range(p+1, len(node_list)):
        if p==q:
            continue
        snode=node_list[p]
        rnode=node_list[q]
        latency_bin=env_vars["OSU_LATENCY"]
        bw_bin=env_vars["OSU_BW"]

        latency_file=f"{snode}to{rnode}_latency.txt"
        bw_file=f"{snode}to{rnode}_bw.txt"
        latency_file_rev=f"{rnode}to{snode}_latency.txt"
        bw_file_rev=f"{rnode}to{snode}_bw.txt"
        # latency_file="lat_file.txt"
        # bw_file="bw_file.txt"

        lbdir=env_vars["LBDIR"]
        os.chdir(lbdir)
        current_files=os.listdir()

        command="mpirun -np 2 --host {},{} {}"

        latency_cmd=command.format(snode, rnode, latency_bin).split(" ")
        bw_cmd=command.format(snode, rnode, bw_bin).split(" ")

        print(latency_cmd)
        print(bw_cmd)

        if (latency_file not in current_files) and (latency_file_rev not in current_files):
            with open(latency_file, "w") as outfile:
                sp.run(latency_cmd, stdout=outfile)

        print(f"Latency between {snode} and {rnode} obtained.")

        if (bw_file not in current_files) and (bw_file_rev not in current_files):
            with open(bw_file, "w") as outfile:
                sp.run(bw_cmd, stdout=outfile)

        print(f"Bandwidth between {snode} and {rnode} obtained.")

        lf=open(latency_file, "r")
        bf=open(bw_file, "r")
        
        lf_lines=lf.readlines()
        bf_lines=bf.readlines()

        # l_count,b_count=0,0
        # l_total,b_total=0,0
        
        p_key=f"{snode}_{rnode}"

        latency_dict[p_key]={}
        bw_dict[p_key]={}
        # print(len(lf_lines))
        for i in range(4, len(lf_lines)):
            # if lf_lines[i].split()[0]!='0':
            #     continue
            k,v=float(lf_lines[i].split()[0]), float(lf_lines[i].split()[1])
            # print(k, v)
            latency_dict[p_key][k]=v
            # l_total+=float(lf_lines[i].split()[1])
            # l_count+=1

        for j in range(4, len(bf_lines)):
            # if bf_lines[j].split()[0]!='1':
            #     continue
            k,v=float(bf_lines[j].split()[0]), float(bf_lines[j].split()[1])
            bw_dict[p_key][k]=v        
            # b_total+=float(bf_lines[j].split()[1]) 
            # b_count+=1
        '''
        avg_latency=l_total/l_count
        avg_bw=b_total/b_count

        key1=f"{snode}_{rnode}"
        key2=f"{rnode}_{snode}"

        latency_dict[key1]=avg_latency
        latency_dict[key2]=avg_latency

        bw_dict[key1]=avg_bw
        bw_dict[key2]=avg_bw       
        '''
node_fp.close()

# print()
# print()

# print("Latencies between nodes:\n")

# for k,v in latency_dict.items():
#     print(k)
#     for a,b in v.items():
#         print(a, " : ", b)
#     print()

#Now need to dissect the communication patterns for different functions 
comm_lines=comm_fp.readlines()

#we have to count the total function calls, and the steps involved in each function.
#we will do both these separately

tag_count=0 #to count the different functions 

for line in comm_lines:
    line=line.split()
    f_tag,step,src,dst=int(line[0]),int(line[1]),int(line[2]),int(line[3])
    tag_count=max(tag_count, f_tag)

#this will store the steps for each of the function
comm_calls=[0]*(tag_count+1) #first one will be blank   

for line in comm_lines:
    line=line.split()
    f_tag,step,src,dst=int(line[0]),int(line[1]),int(line[2]),int(line[3])
    comm_calls[f_tag]=max(comm_calls[f_tag], step)

for i in range(len(comm_calls)):
    comm_calls[i]=[[] for j in range(comm_calls[i]+1)]

for line in comm_lines:
    line=line.split()
    # f_tag,step,src,dst=int(line[0]),int(line[1]),int(line[2]),int(line[3])
    f_tag,step,src,dst,msg_size=int(line[0]),int(line[1]),int(line[2]),int(line[3]),int(line[4])
    # key=f"{src}_{dst}"
    key=f"{src}_{dst}_{msg_size}"
    comm_calls[f_tag][step].append(key)

#print(latency_dict)
#print(bw_dict)
#print(comm_calls)

# for func in comm_calls:
#     idx=0
#     for step in func:
#         print(f"step: {idx}")    
#         print(step)
#         idx+=1
#     print("**************************")

comm_time=0
step_count={}
# print(len(comm_calls))
for i in range(1, len(comm_calls)):
    steps=comm_calls[i]
    idx=0
    # print(len(steps))
    # print(steps)
    # if len(steps)==1:
    #     print(steps)
    if len(steps) in step_count:
        step_count[len(steps)]+=1
    else:
        step_count[len(steps)]=1
    # if len(steps)==1:
    #     # print("true")
    #     print(steps)
    for step in steps:
        # print(f"step: {idx}")
        # print(step)
        idx+=1
        max_this_step=0
        max_comm=''
        max_lat=0
        max_bw=0
        for comm in step:
            comm=comm.split('_')
            src=int(comm[0])
            dst=int(comm[1])
            msg_size=int(comm[2])
            # this_time=0.000219
            # this_time=float(env_vars["SAME_NODE_TIME"])
            this_time=0
            src=rank_to_node[src]
            dst=rank_to_node[dst]
            l,b=0,0
            if src==dst:
                for m,lat in same_node_latency.items():
                    if m>msg_size:
                        break;
                    l=lat;

                for m,bw in same_node_bw.items():
                    if m>msg_size:
                        break;
                    b=bw;

                if msg_size==0:
                    continue 

                this_time=(l+msg_size/b);

            elif src!=dst:
                key=f"{src}_{dst}"
                '''
                    #This was used when the avg latency and bw was being used
                l=latency_dict[key]
                b=bw_dict[key]
                this_time=(l+msg_size/b) #100 is just a placeholder here
                '''
                if key not in latency_dict:
                    key=f"{dst}_{src}"
                
                
                #finding the appropriate latency and bandwidth based on the msg size
                for m,lat in latency_dict[key].items():
                    if m>msg_size:
                        break;
                    l=lat

                for m,bw in bw_dict[key].items():
                    if m>msg_size:
                        break;
                    b=bw

                if msg_size==0:
                    continue
                this_time=(l+msg_size/b)
                # print(this_time)
            if this_time>max_this_step:
                max_comm=comm 
                max_lat=l 
                max_bw=b 
            max_this_step=max(this_time, max_this_step)
        # print()
        # print(f"Comm with max time: {max_comm}")
        # print(f"latency: {max_lat}, bw: {max_bw}")
        # print(f"max time in this step: {max_this_step}")
        # print()
        comm_time+=max_this_step  
        #print(comm_time)      
    # print("***********************")
# print(comm_time)

sr_time=0
send_time=0

sr_lines=sr_file.readlines()
send_lines=send_file.readlines()

current_time=0
for line in sr_lines:
    if line.startswith('*'):
        sr_time=max(sr_time, current_time)
        current_time=0
        continue
    
    line=line.split(' ')
    line[-1]=line[-1].strip('\n')
    s_rank, d_rank, msg = int(line[0]), int(line[1]), int(line[2])

    src=rank_to_node[s_rank]
    dst=rank_to_node[d_rank]
  
    this_time=0

    l,b=0,0
    if src==dst:
        for m,lat in same_node_latency.items():
            if m>msg:
                break;
            l=lat;

        for m,bw in same_node_bw.items():
            if m>msg:
                break;
            b=bw;

        if msg==0:
            continue 

        this_time=(l+msg/b);

    elif src!=dst:
        key=f"{src}_{dst}"
                
        if key not in latency_dict:
            key=f"{dst}_{src}"
            
        #finding the appropriate latency and bandwidth based on the msg size
        for m,lat in latency_dict[key].items():
            if m>msg:
                break;
            l=lat

        for m,bw in bw_dict[key].items():
            if m>msg:
                break;
            b=bw

        if msg==0:
            continue

        this_time=(l+msg/b)

    current_time+=this_time


current_time=0
for line in send_lines:
    if line.startswith('*'):
        send_time=max(send_time, current_time)
        current_time=0
        continue
    
    line=line.split(' ')
    line[-1]=line[-1].strip('\n')
    s_rank, d_rank, msg = int(line[0]), int(line[1]), int(line[2])

    src=rank_to_node[s_rank]
    dst=rank_to_node[d_rank]
    this_time=0

    l,b=0,0
    if src==dst:
        for m,lat in same_node_latency.items():
            if m>msg:
                break;
            l=lat;

        for m,bw in same_node_bw.items():
            if m>msg:
                break;
            b=bw;

        if msg==0:
            continue 

        this_time=(l+msg/b);

    elif src!=dst:
        key=f"{src}_{dst}"
                
        if key not in latency_dict:
            key=f"{dst}_{src}"
            
        #finding the appropriate latency and bandwidth based on the msg size
        for m,lat in latency_dict[key].items():
            if m>msg:
                break;
            l=lat

        for m,bw in bw_dict[key].items():
            if m>msg:
                break;
            b=bw

        if msg==0:
            continue
        
        this_time=(l+msg/b)

    current_time+=this_time

comm_time=comm_time+sr_time+send_time

# print(comm_time)
# print(send_time)
# print(sr_time)

ipmpi_runs_dir=env_vars["IPMPI_RUNS_DIR"]
os.chdir(ipmpi_runs_dir)
# out_file_name=f"comm_{app}_{nodes}_{ppn}_{nx}_{ny}_{nz}.txt"
out_file_name=f"comm_{app}_{nodes}_{ppn}_{nx}_{ny}_{nz}-{it}.txt"
outfile=open(out_file_name, "w")
outfile.write(f"{comm_time}\n")
outfile.close()

node_fp.close()
comm_fp.close()