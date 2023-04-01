from concurrent import futures 

import sys
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


regServerAddr =  config.REG_SERVER_ADDR


class Client:

	def __init__(self, reg_server_stub: registryserver_pb2_grpc.RegistryServerStub) -> None:
		self.id = str(uuid.uuid4())
		self.reg_server_stub = reg_server_stub 
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
		# get all the write replicas
		write_replicas = self.reg_server_stub.GetWriteReplicaList(registryserver_pb2.ClientDetails(client_uuid=self.id))
  
		print("Update Existing File (u) | New File (n)")
		ch = input().lower()
		if ch == 'u':
			print("Enter file uuid: ")
			file_uuid = input()
			print("Enter file name: ")
			file_name = input()
			print("Enter content: ")
			file_content = input()

			print()
			for replica in write_replicas.replica_list:
				print("Replica: ", replica.name, replica.addr)
				with grpc.insecure_channel(replica.addr) as replica_channel:
					replica_stub = replica_pb2_grpc.ReplicaStub(replica_channel)
					write_details = replica_pb2.WriteDetails(name=file_name, uuid=file_uuid, content=file_content)
					response = replica_stub.WriteRequest(write_details)
				print(f"Status: {response.status}")
				print(f"Version: {response.version}")
				print()

		elif ch == 'n':
			file_uuid = str(uuid.uuid4())
			print(f"File uuid: {file_uuid}")
			print("Enter file name: ")
			file_name = input()
			print("Enter content: ")
			file_content = input()
			for replica in write_replicas.replica_list:
				with grpc.insecure_channel(replica.addr) as replica_channel:
					replica_stub = replica_pb2_grpc.ReplicaStub(replica_channel)
					write_details = replica_pb2.WriteDetails(name=file_name, uuid=file_uuid, content=file_content)
					response = replica_stub.WriteRequest(write_details)
				print(f"Status: {response.status}")
				print(f"Version: {response.version}")
				print()

		else:
			print("Invalid Input!")
			return


	def DeleteRequest(self):
		# get all the write replicas
		write_replicas = self.reg_server_stub.GetWriteReplicaList(registryserver_pb2.ClientDetails(client_uuid=self.id))

		print("Enter the uuid of the file you want to request:")
		file_uuid = input() 
		version = str(datetime.fromtimestamp(time.time()))

		# delete from all write replicas
		for replica in write_replicas.replica_list:
			with grpc.insecure_channel(replica.addr) as replica_channel:
				replica_stub = replica_pb2_grpc.ReplicaStub(replica_channel)
				response = replica_stub.DeleteRequest(replica_pb2.DeleteDetails(uuid=file_uuid, version=version))
				print("\tDeleting from replica: " , replica.name)
				print("\tResponse status: ", response.status)
				print()


		print(f"Status: {response.status}")
		# print(f"Name: {response.name}")
		# print(f"Content: {response.content}")
		# print(f"Version: {response.version}")
		print()

	def ReadRequest(self):
		# get all the read replicas
		read_replicas = self.reg_server_stub.GetReadReplicaList(registryserver_pb2.ClientDetails(client_uuid=self.id))

		print("Enter the uuid of the file you want to request:")
		file_uuid = input() 
		
		latestResponse = None
		# query all the read replicas and get the latest version
		for replica in read_replicas.replica_list:
			print("Reading from replica: " , replica.name)
			with grpc.insecure_channel(replica.addr) as replica_channel:
				replica_stub = replica_pb2_grpc.ReplicaStub(replica_channel)
				response = replica_stub.ReadRequest(replica_pb2.ReadDetails(uuid=file_uuid))
				print("Response status: ", response.status)
				# 
				if(response.version == ""):
					continue
				elif latestResponse is None:
					latestResponse = response
					print("Response version: ", response.version)
				else:
					print("Latest Response version: ", latestResponse.version)
					print("Response version: ", response.version)
					prevDatetime = datetime.strptime(latestResponse.version, '%Y-%m-%d %H:%M:%S.%f')
					currentDatetime = datetime.strptime(response.version, '%Y-%m-%d %H:%M:%S.%f')
					if currentDatetime > prevDatetime:
						latestResponse = response


		print("Latest response: ")
		if(latestResponse == None):
			print("No file found!")
			return

		print(f"Status: {latestResponse.status}")
		if(latestResponse.status == "SUCCESS"):
			print(f"Name: {latestResponse.name}")
			print(f"Content: {latestResponse.content}")
			print(f"Version: {latestResponse.version}")
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
		sys.stdout.flush()
		sys.stderr.flush()

	sys.stdout.flush()
	sys.stderr.flush()
	