from concurrent import futures 
import grpc
import random
import registryserver_pb2
import registryserver_pb2_grpc
import replica_pb2
import replica_pb2_grpc
import os
import shutil
import subprocess
import config


class RegistryServer(registryserver_pb2_grpc.RegistryServerServicer):
	def __init__(self, N, Nw, Nr) -> None:
		super().__init__()
		self.N = N
		self.Nw = Nw
		self.Nr = Nr

		self.replicalist = []
		# to connect with the primary stub
		self.primary_replica_stub = None
		self.primary_replica = registryserver_pb2.ReplicaDetails(name="none", addr="none")

		self.setupFileSystem()

	def setupFileSystem(self):
		subprocess.run("./clean_file_system.sh")


	def RegisterReplica(self, request: registryserver_pb2.ReplicaDetails, context):
		print(f"REPLICA live request: {request.name} -> {request.addr}")

		if(len(self.replicalist) == self.N):
			print("Already registered N replicas!")
			return registryserver_pb2.RequestStatus(status=False)

		self.replicalist.append(request)

		# print details of all replicas
		print("All registered replicas: ")
		for replica in self.replicalist:
			print("\t" + replica.name + ". " + replica.addr)
		print()

		return registryserver_pb2.RequestStatus(status=True)

	# ---------------------------------------------------------
	# Current assumption is that enough replicas are registered
	# ---------------------------------------------------------
	def GetReplicaList(self, request: registryserver_pb2.ClientDetails, context):
		print(f"SERVER LIST REQUEST FROM {request.client_uuid}")
		if(len(self.replicalist) < self.N):
			print("Not enough replicas registered!")
   
		rlist = registryserver_pb2.ReplicaList()
		rlist.replica_list.extend(self.replicalist)
		return rlist
	
	def GetReadReplicaList(self, request: registryserver_pb2.ClientDetails, context):
		print(f"SERVER LIST READ REQUEST FROM {request.client_uuid}")
		if(len(self.replicalist) < self.N):
			print("Not enough replicas registered!")
   
		# Randomly select Nr replicas for read
		readlist = random.sample(self.replicalist, self.Nr)

		rlist = registryserver_pb2.ReplicaList()
		rlist.replica_list.extend(readlist)
		return rlist
	
	def GetWriteReplicaList(self, request: registryserver_pb2.ClientDetails, context):
		print(f"SERVER LIST WRITE REQUEST FROM {request.client_uuid}")
		if(len(self.replicalist) < self.N):
			print("Not enough replicas registered!")

		# Randomly select Nw replicas for write
		writelist = random.sample(self.replicalist, self.Nw)
   
		rlist = registryserver_pb2.ReplicaList()
		rlist.replica_list.extend(writelist)
		return rlist

	
def serve(N, Nw, Nr):
	port = config.REG_SERVER_PORT
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=12))
	registryserver_pb2_grpc.add_RegistryServerServicer_to_server(RegistryServer(N, Nw, Nr), server)
	server.add_insecure_port('[::]:' + port)
	server.start()
	print("Registry Server started, listening on " + port)
	server.wait_for_termination()
 
if __name__ == '__main__':
	N = int(input("Enter number of replicas: "))
	Nw = int(input("Enter number of write replicas: "))
	Nr = int(input("Enter number of read replicas: "))

	# condition for quorum should be satisfied:
	if(Nw + Nr < N or Nw < N/2):
		print("Quorum condition not satisfied!")
		exit()

	serve(N, Nw, Nr)