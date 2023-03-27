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


regServerAddr =  config.REG_SERVER_ADDR


class Client:

	def __init__(self, reg_server_stub: registryserver_pb2_grpc.RegistryServerStub) -> None:
		self.id = str(uuid.uuid4())
		self.reg_server_stub = reg_server_stub 
		self.primary_replica_details = self.reg_server_stub.GetPrimaryReplica(registryserver_pb2.Empty())
		primary_replica_channel = grpc.insecure_channel(self.primary_replica_details.addr) 
		self.primary_replica_stub = replica_pb2_grpc.ReplicaStub(primary_replica_channel)
		self.replica_list = None
		self.GetReplicaList()
		
		# self.pr

	def GetReplicaList(self):
		response = self.reg_server_stub.GetReplicaList(registryserver_pb2.Empty())
		self.replica_list = response
		print("\nReplicas: ")
		for replica in self.replica_list:
			print(f"name: {replica.name}, addr: {replica.addr}")
		print()
	
	def WriteRequest(self): 
		print("Update Existing File (u) | New File (n)")
		ch = input().lower()
		if ch == 'u':
			print("Enter file uuid: ")
			file_uuid = input()
			print("Enter file name: ")
			file_name = input()
			print("Enter content: ")
			file_content = input()
			write_details = replica_pb2.WriteDetails(name=file_name, uuid=file_uuid, content=file_content)
			self.primary_replica_stub.WriteRequest(write_details)
		elif ch == 'n':
			file_uuid = str(uuid.uuid4())
			print(f"File uuid: {file_uuid}")
			print("Enter file name: ")
			file_name = input()
			print("Enter content: ")
			file_content = input()
			write_details = replica_pb2.WriteDetails(name=file_name, uuid=file_uuid, content=file_content)
			self.primary_replica_stub.WriteRequest(write_details)
		else:
			print("Invalid Input!")




if __name__ == '__main__':
	ch = 'x'
	registryChannel = grpc.insecure_channel(regServerAddr)
	registryStub = registryserver_pb2_grpc.RegistryServerStub(registryChannel)
	client = Client(registryStub)
	while(ch != 'q'):
		print("---------------####----------------")
		print("Get replica list (g) | Write (j) | Leave Server (l) | Get Article (a) | Publish (p) | Quit (q):")
		ch = input().lower()
		if(ch == 'q'):
			break 
		elif(ch == 'g'):
			client.GetReplicaList()
		elif(ch == 'w'):
			client.WriteRequest()
		elif(ch == 'l'):
			client.LeaveServer()
		elif(ch == 'a'):
			client.GetArticles()
		elif(ch == 'p'):
			client.PublishArticle()
		else:
			print("Invalid input")
		print("-----------------------------------")
	