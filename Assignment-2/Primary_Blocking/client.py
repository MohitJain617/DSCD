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
		response = self.reg_server_stub.GetReplicaList(registryserver_pb2.ClientDetails(client_uuid=self.id))
		self.replica_list = response.replica_list
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
			write_details = replica_pb2.WriteDetails(name=file_name, uuid=file_uuid, content=file_content, version="")
			response = self.primary_replica_stub.WriteRequest(write_details)
		elif ch == 'n':
			file_uuid = str(uuid.uuid4())
			print(f"File uuid: {file_uuid}")
			print("Enter file name: ")
			file_name = input()
			print("Enter content: ")
			file_content = input()
			write_details = replica_pb2.WriteDetails(name=file_name, uuid=file_uuid, content=file_content, version="")
			response = self.primary_replica_stub.WriteRequest(write_details)
		else:
			print("Invalid Input!")
			return
		# print response
		print(f"Status: {response.status}")
		print(f"Name: {response.name}")
		print(f"Content: {response.content}")
		print(f"Version: {response.version}")
		print()


		

	def ReadRequest(self):
		print("Replica list: id | name | ip:port")
		for id, replica in enumerate(self.replica_list):
			print(str(id) + " | " +  replica.name + " | " + replica.addr) 
		
		print("Enter the id of replica you want to query: ")
		replica_id = input()
		if replica_id.isnumeric():
			replica_id = int(replica_id)
			if replica_id >= 0 and replica_id < len(self.replica_list):
				print("Enter the uuid of the file you want to request:")
				file_uuid = input() 
				with grpc.insecure_channel(self.replica_list[replica_id].addr) as replica_channel:
					replica_stub = replica_pb2_grpc.ReplicaStub(replica_channel)
					response = replica_stub.ReadRequest(replica_pb2.ReadDetails(uuid=file_uuid))

				print(f"Status: {response.status}")
				print(f"Name: {response.name}")
				print(f"Content: {response.content}")
				print(f"Version: {response.version}")
				print()
			else:
				print("Invalid replica id!\n")
				return
		else:
		
			print("Invalid replica id!\n")
			return
	
	def DeleteRequest(self):

		print("Enter the uuid of the file you want to request:")
		file_uuid = input() 

		response = self.primary_replica_stub.DeleteRequest(replica_pb2.DeleteDetails(uuid=file_uuid, version=""))

		print(f"Status: {response.status}")
		# print(f"Name: {response.name}")
		# print(f"Content: {response.content}")
		# print(f"Version: {response.version}")
		print()
			

		




if __name__ == '__main__':
	ch = 'x'
	registryChannel = grpc.insecure_channel(regServerAddr)
	registryStub = registryserver_pb2_grpc.RegistryServerStub(registryChannel)
	client = Client(registryStub)
	while(ch != 'q'):
		print("---------------####----------------")
		print("Get replica list (g) | Write (w) | Read (r) | Delete (d) | Quit (q):")
		ch = input().lower()
		if(ch == 'q'):
			break 
		elif(ch == 'g'):
			client.GetReplicaList()
		elif(ch == 'w'):
			client.WriteRequest()
		elif(ch == 'r'):
			client.ReadRequest()
		elif(ch == 'd'):
			client.DeleteRequest()
		else:
			print("Invalid input")
		print("-----------------------------------")
	