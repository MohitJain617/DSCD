from concurrent import futures 

import grpc
import registryserver_pb2
import registryserver_pb2_grpc
import replica_pb2
import replica_pb2_grpc
from datetime import date
from datetime import datetime
import os
import uuid

regServerAddr = 'localhost:50051'

class Replica(replica_pb2_grpc.ReplicaServicer):
	def __init__(self, name, ip, port) -> None:
		super().__init__()
		self.isPrimary = False
		self.primaryReplicaAddr = None
		self.replicaList = []
		self.name = name
		self.ip = ip
		self.port = port
		self.uuid_name =  str(uuid.uuid4())
		self.filesytem_root = '' # All data of the replica is store here
		self.createFileSystem()
	
	# creates the root files system
	def createFileSystem(self):
		self.filesytem_root = "./" + self.name + "_" + self.port + "_" + self.uuid_name
		os.mkdir(self.filesytem_root)

	def RegisterReplica(self):
		with grpc.insecure_channel(regServerAddr) as channel:
			stub = registryserver_pb2_grpc.RegistryServerStub(channel)
			response = stub.RegisterReplica(registryserver_pb2.ReplicaDetails(name=self.name,addr=f"{self.ip}:{self.port}"))
		
		# if returned address is -1, the connection failed
		if(response.addr == "-1"):
			return False

		# Update primary replica details
		self.primaryReplicaAddr = response.addr
		if(response.name == self.name and response.addr == f"{self.ip}:{self.port}"):
			self.isPrimary = True

		return True
	
	def UpdateReplicaList(self, request, context):
		self.replicaList.append(request)
		for repl in self.replicaList:
			print(repl.name + ". " + repl.addr)
		return replica_pb2.RequestStatus(status=True)


def serve(port, s):
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=15))
	replica_pb2_grpc.add_ReplicaServicer_to_server(s, server)
	server.add_insecure_port('[::]:' + port)
	server.start()
	print("Server started, listening on " + port)
	server.wait_for_termination()
 
if __name__ == '__main__':
	name = input("Enter replica name: ")
	port = input("Enter port:")
	s = Replica(name, 'localhost', port)
	if(s.RegisterReplica()):
		serve(port, s)
		