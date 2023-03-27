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
import config

regServerAddr = config.REG_SERVER_ADDR

class Replica(replica_pb2_grpc.ReplicaServicer):
	def __init__(self, name, ip, port) -> None:
		super().__init__()
		self.is_primary = False
		self.primaryReplicaAddr = None
		self.replicaList = [] # list of type ReplicaDetails 
		self.name = name
		self.ip = ip
		self.port = port
		self.uuid_name =  str(uuid.uuid4())
		self.filesytem_root = '' # All data of the replica is store here
		self.createFileSystem()
		self.is_primary = False
		self.filename_to_uuid = {} # if unset then filename free to use 
		self.uuid_to_file = {}
	
	# creates the root files system
	def createFileSystem(self):
		self.filesytem_root = "./file_system/" + self.name + "_" + self.port + "_" + self.uuid_name
		os.mkdir(self.filesytem_root)

	def RegisterReplica(self):
		with grpc.insecure_channel(regServerAddr) as channel:
			reg_server_stub = registryserver_pb2_grpc.RegistryServerStub(channel)
			response = reg_server_stub.RegisterReplica(registryserver_pb2.ReplicaDetails(name=self.name,addr=f"{self.ip}:{self.port}"))
		
		# if returned address is -1, the connection failed
		if(response.addr == "-1"):
			return False

		# Update primary replica details
		self.primaryReplicaAddr = response.addr
		if(response.name == self.name and response.addr == f"{self.ip}:{self.port}"):
			self.is_primary = True

		return True
	
	def UpdateReplicaList(self, request : replica_pb2.ReplicaDetails, context):
		self.replicaList.append(request)
		for repl in self.replicaList:
			print(repl.name + ". " + repl.addr)
		return replica_pb2.RequestStatus(status=True)
	
	def canWrite(self, request):
		can_write = True
		status = "SUCCESS"

		if request.uuid in self.uuid_to_file:
			if os.path.exists(self.filesytem_root + "/" + self.uuid_to_file[request.uuid]):
				# update 
				can_write = True
				status = "SUCCESS" 
			else:
				# DELETED
				can_write = False
				status = "CAN\'T UPDATE DELETED FILE"
		else: 
			if request.name in self.filename_to_uuid:
				can_write = False
				status = "FILENAME IN USE"
			else:
				can_write = True 
				status = "SUCCESS"

		return can_write, status

	# Handles write request 
	def WriteRequest(self, request: replica_pb2.WriteDetails, context):
		can_write, status = True, "SUCCESS"
		if self.is_primary == True:
			# Write and send write reqs to other replcas 
			can_write, status = self.canWrite(request)
			if can_write == False:
				return replica_pb2.WriteResponse(status=status)
			else:
				self.filename_to_uuid[request.name] = request.uuid
				self.uuid_to_file[request.uuid] = request.name

				f = open(self.filesytem_root + "/" + request.name, "w")
				f.write(request.content)
				f.close()

				for replica in self.replicaList:
					# replica_addr = replica.ad
					try:
						with grpc.insecure_channel(replica.addr) as channel:
							replica_stub = replica_pb2_grpc.ReplicaStub(channel)
							response = replica_stub.WriteRequest(request)
							if(response.status  != "SUCCESS"):
								print("Write propogation failed!")
								status = "WRITE PROP FAILED"
								return replica_pb2.WriteResponse(status=status)
						

					except Exception as e:
						print(f"Couldn't Connect With Replica {replica.addr}!")
						# return


				
		else: 
			self.filename_to_uuid[request.name] = request.uuid
			self.uuid_to_file[request.uuid] = request.name
			f = open(self.filesytem_root + "/" + request.name, "w")
			f.write(request.content)
			f.close()
			return replica_pb2.WriteResponse(status="SUCCESS")

		return replica_pb2.WriteResponse(status=status)




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
		