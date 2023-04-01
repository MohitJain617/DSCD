import subprocess
import time

N_Replicas = 4

Replica_info = [
    "A 50001",
    "B 50002",
    "C 50003",
    "D 50004",
]

subprocess.Popen(['start', 'cmd', '/c', 'python registry_server.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

time.sleep(1)

for i in range(N_Replicas) :
    name = chr(ord('A') + i)
    port = 50000 + (i+1)
    command = "python replica.py " + str(name) + " " + str(port) 
    subprocess.Popen(['start', 'cmd', '/c', command], shell=True)
    time.sleep(1)

subprocess.Popen(['start', 'cmd', '/c', 'python client1.py' + " " + Replica_info[i]], shell=True)