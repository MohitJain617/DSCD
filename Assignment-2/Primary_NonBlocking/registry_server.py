from concurrent import futures 
import grpc
import registryserver_pb2
import registryserver_pb2_grpc
import replica_pb2
import replica_pb2_grpc
import os
import subprocess
import config


class RegistryServer(registryserver_pb2_grpc.RegistryServerServicer):
	def __init__(self) -> None:
		super().__init__()
		self.primary_replica = registryserver_pb2.ReplicaDetails(name="none", addr="none")
		# self.primary_replica.addr 
		self.replicalist = []
		# to connect with the primary stub
		self.primary_replica_stub = None
		self.setupFileSystem()

	def setupFileSystem(self):
		subprocess.run(".\clean_file_system.bat", shell = True)


	def GetPrimaryReplica(self, request, context):
		return self.primary_replica


	def RegisterReplica(self, request: registryserver_pb2.ReplicaDetails, context):
		
		print(f"\nREPLICA live request: {request.name} -> {request.addr}\n")
		
		if(self.primary_replica.addr == "none"):
			self.primary_replica = request
			self.primary_replica_stub = replica_pb2_grpc.ReplicaStub(grpc.insecure_channel(self.primary_replica.addr))
			print("Primary Replica Registered ! \n")
		
		else:
			response = self.primary_replica_stub.UpdateReplicaList(replica_pb2.ReplicaDetails(name=request.name,addr=request.addr))
			if(response.status == False):
				print("Failed to update Primary Server replica list \n")
			else:
				print("Successfully Registered the Replica and updated Primary Server replica list \n")

		self.replicalist.append(request)

		print("All registered replicas (including primary server): ")
		for replica in self.replicalist:
			print(replica.name + " - " + replica.addr)
		print()

		return self.primary_replica
	

	def GetReplicaList(self, request: registryserver_pb2.ClientDetails, context):
		print(f"SERVER LIST REQUEST FROM {request.client_uuid}")
		rlist = registryserver_pb2.ReplicaList()
		rlist.replica_list.extend(self.replicalist)
		return rlist
	
	
def serve():
	
	port = config.REG_SERVER_PORT
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=12))
	registryserver_pb2_grpc.add_RegistryServerServicer_to_server(RegistryServer(), server)
	
	server.add_insecure_port('[::]:' + port)
	server.start()
	print("\nRegistry Server started, listening on " + port)

	try:
		server.wait_for_termination()
	except KeyboardInterrupt:
		server.stop(0)
 
if __name__ == '__main__':
    serve()