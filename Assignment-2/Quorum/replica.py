from concurrent import futures 

import time
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
import pathlib

regServerAddr = config.REG_SERVER_ADDR

class Replica(replica_pb2_grpc.ReplicaServicer):
	def __init__(self, name, ip, port) -> None:
		super().__init__()
		self.name = name
		self.ip = ip
		self.port = port
		self.uuid_name =  str(uuid.uuid4())
		self.filesytem_root = '' # All data of the replica is store here
		self.createFileSystem()
		self.filename_to_uuid = {}
		self.uuid_to_file = {}
		self.uuid_to_version = {}
	
	# creates the root files system
	def createFileSystem(self):
		self.filesytem_root = "./file_system/" + self.name + "_" + self.port + "_" + self.uuid_name
		os.mkdir(self.filesytem_root)

	def RegisterReplica(self):
		with grpc.insecure_channel(regServerAddr) as channel:
			reg_server_stub = registryserver_pb2_grpc.RegistryServerStub(channel)
			response = reg_server_stub.RegisterReplica(registryserver_pb2.ReplicaDetails(name=self.name,addr=f"{self.ip}:{self.port}"))

		# if returned address is -1, the connection failed
		if(response.status == False):
			print("Failed to register replica with registry server.")
		else:
			print("Replica registered with registry server.")

		return True
	
	def canWrite(self, request):
		can_write = True
		status = "SUCCESS"

		if request.uuid in self.uuid_to_file:
			if self.uuid_to_file[request.uuid] != "" and os.path.exists(self.filesytem_root + "/" + self.uuid_to_file[request.uuid]):
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
	def WriteRequest(self, request: replica_pb2.WriteDetails, context) -> replica_pb2.WriteResponse:
		can_write, status = self.canWrite(request)
		if can_write == False:
			return replica_pb2.WriteResponse(status=status, name=request.name, content=request.content, version="")
		else:
			self.filename_to_uuid[request.name] = request.uuid
			self.uuid_to_file[request.uuid] = request.name

			f = open(self.filesytem_root + "/" + request.name, "w")
			f.write(request.content)
			f.close()

			file_version = pathlib.Path(self.filesytem_root + "/" + request.name).stat().st_mtime
			file_version = str(datetime.fromtimestamp(file_version))
			self.uuid_to_version[request.uuid] = file_version
			request.version = file_version

			return replica_pb2.WriteResponse(status=status, name=request.name, content=request.content, version=file_version)


	def ReadRequest(self, request: replica_pb2.ReadDetails, context) -> replica_pb2.ReadResponse:
		if request.uuid in self.uuid_to_file:
			print("UUID in memory map")
			file_path = self.filesytem_root + '/' + self.uuid_to_file[request.uuid]
			# in memory map 
			if self.uuid_to_file[request.uuid] != '' and os.path.exists(file_path):
				# file not deleted 
				print("file exists")
				file_name = self.uuid_to_file[request.uuid]
				with open(file_path, "r") as f:
					file_content = f.read()
				file_version = self.uuid_to_version[request.uuid]

				return replica_pb2.ReadResponse(status="SUCCESS", name=file_name, content=file_content, version=file_version)
			else: 
				print("file has been deleted")
				version = ""
				if request.uuid in self.uuid_to_version:
					version = self.uuid_to_version[request.uuid]
				# file deleted! 
				status = "FILE ALREADY DELETED"
				return replica_pb2.ReadResponse(status=status, name="", content="", version=version)
		else:
			print("file never created here")
			# file doesn't exist 
			return replica_pb2.ReadResponse(status="NO FILE RECORD", name="", content="", version="")
		
	# Handles delete request 
	def DeleteRequest(self, request: replica_pb2.DeleteDetails, context) -> replica_pb2.DeleteResponse:
		
		# file uuid not in memory map, still we delete for quorum
		if request.uuid not in self.uuid_to_file:
			self.uuid_to_file[request.uuid] = ""
			self.uuid_to_version[request.uuid] = str(datetime.fromtimestamp(time.time()))
			return replica_pb2.DeleteResponse(status="SUCCESS")
		
		# file in uuid map, but deleted
		if self.uuid_to_file[request.uuid] == "":
			return replica_pb2.DeleteResponse(status="File already deleted!")

		os.remove(self.filesytem_root + "/" + self.uuid_to_file[request.uuid])

		self.filename_to_uuid.pop(self.uuid_to_file[request.uuid])
		self.uuid_to_file[request.uuid] = ""
		self.uuid_to_version[request.uuid] = request.version

		return replica_pb2.DeleteResponse(status="SUCCESS")


			




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
		