import grpc 
import registryserver_pb2
import registryserver_pb2_grpc
import server_pb2
import server_pb2_grpc

import uuid

class Client:
	def __init__(self) -> None:
		self.id = str(uuid.uuid1())

	def GetServerList(self, rstub):
		response = rstub.GetServerList()

	def JoinServer(self):
		addr = input("Address of server (ip:port) = ")
		with grpc.insecure_channel(addr) as channel:
			stub = server_pb2_grpc.ServerStub(channel)
			response = stub.JoinServer(server_pb2.ClientDetails(client_uuid=self.id))
			if(response.request_status == True):
				print("SUCCESS")
			else:
				print("FAILED")

	def LeaveServer(self):
		addr = input("Address of server (ip:port) = ")
		with grpc.insecure_channel(addr) as channel:
			stub = server_pb2_grpc.ServerStub(channel)
			response = stub.JoinServer(server_pb2.ClientDetails(client_uuid=self.id))
			if(response.request_status == True):
				print("SUCCESS")
			else:
				print("FAILED")

	def GetArticles(self):
		addr = input("Address of server (ip:port) = ")
		tag = input("Article tag (sports, fashion, politics, else all)").lower() 
		# tag
		reqArticle = server_pb2.RequestMessage(client_uuid=self.id)
		if(tag == 'sports'):
			reqArticle.SPORTS = True
		elif(tag == 'fashion'):
			reqArticle.FASHION = True 
		elif(tag == 'politics'):
			reqArticle.POLITICS = True 
		else:
			reqArticle.allTags = True
		# author 
		author = input("Author name (or blank):")
		reqArticle.author = author
		# date 
		day = int(input("day: "))
		month = int(input("month: "))
		year = int(input("year: "))
		reqArticle.day = day
		reqArticle.month = month
		reqArticle.year = year
		
		with grpc.insecure_channel(addr) as channel:
			stub = server_pb2_grpc.ServerStub(channel)
			response = stub.GetArticles(reqArticle)
			if(response.status == False):
				print("FAILED")
			else:
				# print articles
				for article in response.articles:
					print()
					print()
					print()
	def PublishArticles(self):
		pass
		
if __name__== '__main__':
	client = Client()
	ch = 'x'
	registryServerAddr = 'localhost:50051'
	registryChannel = grpc.insecure_channel(registryServerAddr)
	registryStub = registryserver_pb2_grpc.RegistryServerStub(registryChannel)
	while(ch != 'q'):
		print("---------------####----------------")
		print("Get server list (g) | Join Server (j) | Get Article (a) | Publish (p) | Quit (q)")
		ch = input().lower()
		if(ch == 'q'):
			break 
		elif(ch == 'g'):
			client.GetArticles(registryStub)
		elif(ch == 'j'):
			addr = input("Address of server (ip:port) = ")
		elif(ch == 'a'):
			pass
		elif(ch == 'p'):
			pass
		else:
			print("Invalid input")
		print("-----------------------------------")
	