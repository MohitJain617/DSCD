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


regServerAddr =  config.REG_SERVER_ADDR

MANUAL_TESTING = False

class Client:

	def __init__(self, reg_server_stub: registryserver_pb2_grpc.RegistryServerStub, testfile_reader) -> None:
		self.id = str(uuid.uuid4())
		self.reg_server_stub = reg_server_stub 
		self.replica_list = None
		self.GetReplicaList()
		self.uuids = []
		self.test_file = testfile_reader

	def GetReplicaList(self):
		response = self.reg_server_stub.GetReplicaList(registryserver_pb2.ClientDetails(client_uuid=self.id))
		self.replica_list = response.replica_list
		print("\nReplicas: ")
		for replica in self.replica_list:
			print(f"Name: {replica.name}, Addr: {replica.addr}")
		print()
	
	def WriteRequest(self): 
		print("Replica list: id | name | ip:port")
		for id, replica in enumerate(self.replica_list):
			print(str(id) + " | " +  replica.name + " | " + replica.addr) 
		print()
		
		if(MANUAL_TESTING) :
			replica_id = input("Enter the id of replica you want to query: ")
		else:
			replica_id = self.test_file.readline().strip().lower()
			print("Enter the id of replica you want to query: " + str(replica_id))

		if replica_id.isnumeric() == False or (int(replica_id) < 0 or int(replica_id) >= len(self.replica_list)):
			print("Invalid Replica ID!")
			return

		replica_id = int(replica_id)

		with grpc.insecure_channel(self.replica_list[replica_id].addr) as channel:
			
			rep_stub = replica_pb2_grpc.ReplicaStub(channel)

			print("Update Existing File (u) | New File (n)")
			
			if(MANUAL_TESTING) :
				ch = input().lower()
			else :
				ch = self.test_file.readline().strip().lower()

			print(ch)

			if ch == 'u':

				if(MANUAL_TESTING) : 
					file_uuid = input("Enter file uuid: ")
					file_name = input("Enter file name: ")
					file_content = input("Enter content: ")

				else :
					file_uuid = self.uuids[0]
					file_name = self.test_file.readline().strip()
					file_content = self.test_file.readline().strip()
					print("Enter file uuid: " + str(file_uuid))
					print("Enter file name: " + str(file_name))
					print("Enter content: " + str(file_content))

				write_details = replica_pb2.WriteDetails(name=file_name, uuid=file_uuid, content=file_content, version="", primary_hop=False)
				response = rep_stub.WriteRequest(write_details)

			elif ch == 'n':
				
				file_uuid = str(uuid.uuid4())
				self.uuids.append(file_uuid)
				print(f"File uuid: {file_uuid}")

				if(MANUAL_TESTING) : 
					file_name = input('Enter file name : ')
					file_content = input("Enter content : ")
				else :
					file_name = self.test_file.readline().strip()
					file_content = self.test_file.readline().strip()
					print("Enter file name: " + str(file_name))
					print("Enter content: " + str(file_content))

				write_details = replica_pb2.WriteDetails(name=file_name, uuid=file_uuid, content=file_content, version="", primary_hop=False)
				response = rep_stub.WriteRequest(write_details)

			else:
				print("Invalid Input!")
				return
			
			# print response
			print(f"\nStatus: {response.status}")

			if(response.status == 'SUCCESS') :
				print(f"Name: {response.name}")
				print(f"Content: {response.content}")
				print(f"UUID: {response.uuid}")
				print(f"Version: {response.version}")
			print()


	def ReadRequest(self):
		
		print("Replica list: id | name | ip:port")
		for id, replica in enumerate(self.replica_list):
			print(str(id) + " | " +  replica.name + " | " + replica.addr) 
		print()
		
		if(MANUAL_TESTING) :
			replica_id = input("Enter the id of replica you want to query: ")
		else:
			replica_id = self.test_file.readline().strip()
			print("Enter the id of replica you want to query: " + str(replica_id))

		if replica_id.isnumeric():
			replica_id = int(replica_id)
			if replica_id >= 0 and replica_id < len(self.replica_list):
				
				if(MANUAL_TESTING) : 
					file_uuid = input("Enter the uuid of the file you want to request: ") 

				else:
					file_uuid = self.uuids[-1]   # Kind of Hardcoded
					print("Enter the uuid of the file you want to request: " + file_uuid)

				with grpc.insecure_channel(self.replica_list[replica_id].addr) as replica_channel:
					replica_stub = replica_pb2_grpc.ReplicaStub(replica_channel)
					response = replica_stub.ReadRequest(replica_pb2.ReadDetails(uuid=file_uuid))
				
				print(f"\nStatus: {response.status}")
				if(response.status == 'SUCCESS') : 
					print(f"Name: {response.name}")
					print(f"Content: {response.content}")
					print(f"Version: {response.version}")
					print()
			else:
				print("\nInvalid replica id!\n")
				return
		else:
		
			print("\nInvalid replica id!\n")
			return
	
	def DeleteRequest(self):
		
		print("Replica list: id | name | ip:port")
		for id, replica in enumerate(self.replica_list):
			print(str(id) + " | " +  replica.name + " | " + replica.addr) 
		
		print()

		if(MANUAL_TESTING) :
			replica_id = input("Enter the id of replica you want to query: ")
		else:
			replica_id = self.test_file.readline().strip().lower()
			print("Enter the id of replica you want to query: " + str(replica_id))

		if replica_id.isnumeric() == False or (int(replica_id) < 0 or int(replica_id) >= len(self.replica_list)):
			print("Invalid Replica ID!")
			return

		replica_id = int(replica_id)

		with grpc.insecure_channel(self.replica_list[replica_id].addr) as channel:
			rep_stub = replica_pb2_grpc.ReplicaStub(channel)

			if(MANUAL_TESTING) : 
				file_uuid = input("Enter the uuid of the file you want to request: ") 

			else:
				file_uuid = self.uuids[-1]   # Kind of Hardcoded
				print("Enter the uuid of the file you want to request: " + file_uuid)

			version = str(datetime.fromtimestamp(time.time()))
			response = rep_stub.DeleteRequest(replica_pb2.DeleteDetails(uuid=file_uuid, version=version, primary_hop=False))

			print(f"\nStatus: {response.status}")
			# print(f"Name: {response.name}")
			# print(f"Content: {response.content}")
			# print(f"Version: {response.version}")
			print()
			

if __name__ == '__main__':
	
	ch = 'x'
	file = open('testing_input_client.txt', 'r')
	registryChannel = grpc.insecure_channel(regServerAddr)
	registryStub = registryserver_pb2_grpc.RegistryServerStub(registryChannel)
	client = Client(registryStub, file)
	
	while(ch != 'q'):
		
		print("-----------------------------------------")
		print("Get replica list (g) | Write (w) | Read (r) | Delete (d) | Quit (q):")

		if(MANUAL_TESTING) :
			ch = input().lower()

		else:
			ch = file.readline().strip().lower()

		if(not ch) :
			ch = input()
			break
		
		print(ch)
		time.sleep(5)

		if(ch == 'q'):
			break 
		elif(ch == 'g'):
			print('\n[GET REPLICAS REQUEST]\n')
			client.GetReplicaList()
		elif(ch == 'w'):
			print('\n[WRITE REQUEST]\n')
			client.WriteRequest()
		elif(ch == 'r'):
			print('\n[READ REQUEST]\n')
			client.ReadRequest()
		elif(ch == 'd'):
			print('\n[DELETE REQUEST]\n')
			client.DeleteRequest()
		else:
			print("Invalid input")

		print("-----------------------------------")
	