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
import pathlib
import time
import sys

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
			print(repl.name + " | " + repl.addr)
		return replica_pb2.RequestStatus(status=True)
	
	def canWrite(self, request: replica_pb2.WriteDetails):
		can_write = True
		status = "SUCCESS"

		if request.uuid in self.uuid_to_file:
			if self.uuid_to_file[request.uuid] != "" and os.path.exists(self.filesytem_root + "/" + request.name):
				# update 
				can_write = True
				status = "SUCCESS" 
			elif self.uuid_to_file[request.uuid] == "":
				# DELETED
				can_write = False
				status = "CAN\'T UPDATE DELETED FILE"
			else:
				can_write = False
				status = "WRONG FILE NAME"
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
		if request.primary_hop == False and self.is_primary == False:
			with grpc.insecure_channel(self.primaryReplicaAddr) as prim_channel:
				request.primary_hop = True
				prim_stub = replica_pb2_grpc.ReplicaStub(prim_channel)
				return prim_stub.WriteRequest(request)
		
		can_write, status = True, "SUCCESS"
		if self.is_primary == True:
			# Write and send write reqs to other replcas 
			can_write, status = self.canWrite(request)
			request.primary_hop = True
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

				for replica in self.replicaList:
					# replica_addr = replica.ad
					try:
						with grpc.insecure_channel(replica.addr) as channel:
							replica_stub = replica_pb2_grpc.ReplicaStub(channel)
							response = replica_stub.WriteRequest(request)
							if(response.status  != "SUCCESS"):
								print("Write propogation failed!")
								status = "WRITE PROP FAILED"
								return replica_pb2.WriteResponse(status=status, name=request.name, content=request.content, version=file_version)
						

					except Exception as e:
						print(f"Couldn't Connect With Replica {replica.addr}!")
						print(e)
						# return


				
		else: 
			self.filename_to_uuid[request.name] = request.uuid
			self.uuid_to_file[request.uuid] = request.name
			f = open(self.filesytem_root + "/" + request.name, "w")
			f.write(request.content)
			f.close()
			self.uuid_to_version[request.uuid] = request.version
			file_version = request.version
			return replica_pb2.WriteResponse(status="SUCCESS", name=request.name, content=request.content, version=file_version)

		return replica_pb2.WriteResponse(status=status, name=request.name, content=request.content, version=file_version)

	def ReadRequest(self, request: replica_pb2.ReadDetails, context) -> replica_pb2.ReadResponse:
		
		# if request.uuid in self.uuid_to_file and self.uuid_to_file[request.uuid] != "":
		# 	file_path = self.filesytem_root + '/' + self.uuid_to_file[request.uuid]
		# 	# in memory map 
		# 	if os.path.exists(file_path):
		# 		# file not deleted 
		# 		file_name = self.uuid_to_file[request.uuid]
		# 		with open(file_path, "r") as f:
		# 			file_content = f.read()
		# 		file_version = self.uuid_to_version[request.uuid]

		# 		return replica_pb2.ReadResponse(status="SUCCESS", name=file_name, content=file_content, version=file_version)
		# 	else: 
		# 		# file deleted! 
		# 		status = "FILE ALREADY DELETED"
		# 		return replica_pb2.ReadResponse(status=status, name="", content="", version="")
		# else:
		# 	# file doesn't exist 
		# 	status = "FILE DOES NOT EXIST"
		# 	return replica_pb2.ReadResponse(status=status, name="", content="", version="")


		if request.uuid not in self.uuid_to_file :
			return replica_pb2.ReadResponse(status='FILE DOES NOT EXIST', name=None, content=None, version=None)
		
		elif self.uuid_to_file[request.uuid] == '' :
			status = "FILE HAS BEEN DELETED"
			return replica_pb2.ReadResponse(status=status, name=None, content=None, version=None)

		else :
			
			file_path = self.filesytem_root + '/' + self.uuid_to_file[request.uuid]
			
			if os.path.exists(file_path):
				
				# file not deleted 
				file_name = self.uuid_to_file[request.uuid]
				with open(file_path, "r") as f:
					file_content = f.read()
				file_version = self.uuid_to_version[request.uuid]
				return replica_pb2.ReadResponse(status="SUCCESS", name=file_name, content=file_content, version=file_version)
			
			else: 
				# file deleted! 
				status = "BAD HAPPENED"
				return replica_pb2.ReadResponse(status=status, name=None, content=None, version=None)


	# Handles delete request 
	def DeleteRequest(self, request: replica_pb2.DeleteDetails, context) -> replica_pb2.DeleteResponse:
		if request.primary_hop == False and self.is_primary == False:
			with grpc.insecure_channel(self.primaryReplicaAddr) as prim_channel:
				request.primary_hop = True
				prim_stub = replica_pb2_grpc.ReplicaStub(prim_channel)
				return prim_stub.DeleteRequest(request)
		
		if request.uuid not in self.uuid_to_file:
			return replica_pb2.DeleteResponse(status="Invalid UUID!")
		
		if self.uuid_to_file[request.uuid] == "":
			return replica_pb2.DeleteResponse(status="File already deleted!")

		if self.is_primary == True:
			# Delete and send delete reqs to other replcas 
			request.primary_hop = True

			os.remove(self.filesytem_root + "/" + self.uuid_to_file[request.uuid])

			# remove from filename_to_uuid dict as well
			self.filename_to_uuid.pop(self.uuid_to_file[request.uuid])
			self.uuid_to_file[request.uuid] = ""
			new_version = str(datetime.fromtimestamp(time.time()))
			self.uuid_to_version[request.uuid] = new_version

			request.version = new_version

			for replica in self.replicaList:
				# replica_addr = replica.ad
				try:
					with grpc.insecure_channel(replica.addr) as channel:
						replica_stub = replica_pb2_grpc.ReplicaStub(channel)
						response = replica_stub.DeleteRequest(request)
						if(response.status  != "SUCCESS"):
							print("Delete propogation failed!")
							status = "DELETE PROP FAILED"
							return replica_pb2.DeleteResponse(status=status)
					

				except Exception as e:
					print(f"Couldn't Connect With Replica {replica.addr}!")
					print(e)
					# return


				
		else: 

			os.remove(self.filesytem_root + "/" + self.uuid_to_file[request.uuid])

			self.filename_to_uuid.pop(self.uuid_to_file[request.uuid])
			self.uuid_to_file[request.uuid] = ""
			new_version = request.version
			self.uuid_to_version[request.uuid] = new_version

			return replica_pb2.DeleteResponse(status="SUCCESS")

		return replica_pb2.DeleteResponse(status="SUCCESS")

		
			
def serve(port, s):
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=15))
	replica_pb2_grpc.add_ReplicaServicer_to_server(s, server)
	server.add_insecure_port('[::]:' + port)
	server.start()
	print("\nServer " + s.name + " started, listening on " + port + "\n")
	try:
		server.wait_for_termination()
	except KeyboardInterrupt:
		server.stop(0)
 
if __name__ == '__main__':
	
	args = sys.argv

	name = str(args[1])
	port = str(args[2])

	s = Replica(name, 'localhost', port)
	if(s.RegisterReplica()):
		serve(port, s)
		