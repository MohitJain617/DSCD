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
import threading

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
		self.filename_to_uuid = {} # if unset then filename free to use 
		self.uuid_to_file = {}
		self.uuid_to_version = {}
	
	def createFileSystem(self):
		dir_descriptor = self.name + "_" + self.port
		self.filesytem_root = os.path.join('file_system', dir_descriptor)
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
		print('Replica List :')
		for repl in self.replicaList:
			print(repl.name + " - " + repl.addr)
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
				status = "CAN\'T UPDATE A DELETED FILE"
			else:
				can_write = False
				status = "WRONG FILE NAME BAD HAPPENED"
		else: 
			if request.name in self.filename_to_uuid:
				can_write = False
				status = "FILE WITH THE SAME NAME ALREADY EXISTS"
			else:
				can_write = True 
				status = "SUCCESS"

		return can_write, status

	def Write_Update_Backup_Replicas(self, request: replica_pb2.WriteDetails) :
		
		time.sleep(1)
		
		print('Backups Updating ! Waiting for ACK\n')
		
		for replica in self.replicaList:

			time.sleep(10)

			try:
				with grpc.insecure_channel(replica.addr) as channel:
					replica_stub = replica_pb2_grpc.ReplicaStub(channel)
					response = replica_stub.WriteRequest(request)
					if(response.status  != "SUCCESS"):
						print("Write propogation failed!")
						status = "WRITE PROP FAILED"
						return
				
			except Exception as e:
				print(f"Couldn't Connect With Replica {replica.addr}!")
				print(e)
				return
			
			print(replica.name + ' Replica Updated')

	# Handles write request 
	def WriteRequest(self, request: replica_pb2.WriteDetails, context) -> replica_pb2.WriteResponse:
		
		if request.primary_hop == False and self.is_primary == False:
			print("CLIENT Write Request to a Non-Primary Replica -> " + request.uuid + '\n')
			print('Forwarding request to Primary\n')
			with grpc.insecure_channel(self.primaryReplicaAddr) as prim_channel:
				request.primary_hop = True
				prim_stub = replica_pb2_grpc.ReplicaStub(prim_channel)
				return prim_stub.WriteRequest(request)
		
		can_write, status = True, "SUCCESS"
		
		if self.is_primary == True:

			print("CLIENT Write Request to a Primary Replica -> " + request.uuid + "\n")
			# Write and send write reqs to other replcas 
			can_write, status = self.canWrite(request)
			request.primary_hop = True

			if can_write == False:
				return replica_pb2.WriteResponse(status=status, name=request.name, content=request.content, uuid = request.uuid, version="")
			
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

				background_thread = threading.Thread(target=self.Write_Update_Backup_Replicas, args=(request,))
				background_thread.start()

				print('ACKNOWLEDGEMNT Write Completed, back to queried Replica !\n')
				return replica_pb2.WriteResponse(status=status, name=request.name, content=request.content, uuid = request.uuid, version=file_version)
	
		else: 

			print("Backups Update Write Request -> " + request.uuid + "\n")
			self.filename_to_uuid[request.name] = request.uuid
			self.uuid_to_file[request.uuid] = request.name
			f = open(self.filesytem_root + "/" + request.name, "w")
			f.write(request.content)
			f.close()
			self.uuid_to_version[request.uuid] = request.version
			file_version = request.version
			return replica_pb2.WriteResponse(status="SUCCESS", name=request.name, content=request.content, uuid = request.uuid, version=file_version)

	def ReadRequest(self, request: replica_pb2.ReadDetails, context) -> replica_pb2.ReadResponse:
		
		print("CLIENT Read Request -> " + request.uuid + "\n")

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

	def Delete_Update_Backup_Replicas(self, request: replica_pb2.WriteDetails) :
		
		print('Backups Updating ! Waiting for ACK \n')

		for replica in self.replicaList:
				
			time.sleep(10)
			# replica_addr = replica.ad
			try:
				with grpc.insecure_channel(replica.addr) as channel:
					replica_stub = replica_pb2_grpc.ReplicaStub(channel)
					response = replica_stub.DeleteRequest(request)
					if(response.status  != "SUCCESS"):
						print("Delete propogation failed!")
						status = "DELETE PROP FAILED"
						return 
				
			except Exception as e:
				print(f"Couldn't Connect With Replica {replica.addr}!")
				print(e)
				return
			
			print(replica.name + ' Replica Updated Delete')
	
	# Handles delete request 
	def DeleteRequest(self, request: replica_pb2.DeleteDetails, context) -> replica_pb2.DeleteResponse:
		
		if request.primary_hop == False and self.is_primary == False:
			print("CLIENT Delete Request to a Non-Primary Replica -> " + request.uuid + '\n')
			print('Forwarding request to Primary\n')
			with grpc.insecure_channel(self.primaryReplicaAddr) as prim_channel:
				request.primary_hop = True
				prim_stub = replica_pb2_grpc.ReplicaStub(prim_channel)
				return prim_stub.DeleteRequest(request)
		
		if request.uuid not in self.uuid_to_file:
			return replica_pb2.DeleteResponse(status=" FILE DOES NOT EXIST!")
		
		if self.uuid_to_file[request.uuid] == "":
			return replica_pb2.DeleteResponse(status="FILE ALREADY DELETED!")

		if self.is_primary == True:

			print("CLIENT Delete Request to a Primary Replica -> " + request.uuid + "\n")
			# Delete and send delete reqs to other replcas 
			request.primary_hop = True

			os.remove(self.filesytem_root + "/" + self.uuid_to_file[request.uuid])

			# remove from filename_to_uuid dict as well
			self.filename_to_uuid.pop(self.uuid_to_file[request.uuid])
			self.uuid_to_file[request.uuid] = ""
			new_version = str(datetime.fromtimestamp(time.time()))
			self.uuid_to_version[request.uuid] = new_version
			request.version = new_version

			background_thread = threading.Thread(target=self.Delete_Update_Backup_Replicas, args=(request,))
			background_thread.start()

			print('ACKNOWLEDGEMNT Delete Completed, back to queried Replica !\n')
			return replica_pb2.DeleteResponse(status="SUCCESS")
				
		else: 

			print("Backups Update Delete Request -> " + request.uuid + "\n")
			os.remove(self.filesytem_root + "/" + self.uuid_to_file[request.uuid])

			self.filename_to_uuid.pop(self.uuid_to_file[request.uuid])
			self.uuid_to_file[request.uuid] = ""
			new_version = request.version
			self.uuid_to_version[request.uuid] = new_version

			return replica_pb2.DeleteResponse(status="SUCCESS")


def serve(port, s):
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=15))
	replica_pb2_grpc.add_ReplicaServicer_to_server(s, server)
	server.add_insecure_port('[::]:' + port)
	server.start()
	print("\nServer started, listening on " + port + "\n")
	try:
		server.wait_for_termination()
	except KeyboardInterrupt:
		server.stop(0)

 
if __name__ == '__main__':
	name = input("Enter replica name : ")
	port = input("Enter port : ")
	s = Replica(name, 'localhost', port)
	if(s.RegisterReplica()):
		serve(port, s)
		