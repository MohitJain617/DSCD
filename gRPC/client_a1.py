import grpc 
import registryserver_pb2
import registryserver_pb2_grpc
import server_pb2
import server_pb2_grpc

import uuid

regServerAddr = 'localhost:50051'
class Client:
	def __init__(self) -> None:
		self.id = str(uuid.uuid1())

	def GetServerList(self, rstub):
		response = rstub.GetServerList(registryserver_pb2.ClientDetails(client_uuid=self.id))
		for ss in response.server_list:
			print(f"{ss.name} -> {ss.addr}")

	def JoinServer(self):
		addr = input("Address of server (ip:port) = ")
		try:
			with grpc.insecure_channel(addr) as channel:
				stub = server_pb2_grpc.ServerStub(channel)
				response = stub.JoinServer(server_pb2.ClientDetails(client_uuid=self.id))
				if(response.request_status == True):
					print("SUCCESS")
				else:
					print("FAILED")
		except Exception as e:
			print("Invalid address")
			return

	def LeaveServer(self):
		addr = input("Address of server (ip:port) = ")
		try:
			with grpc.insecure_channel(addr) as channel:
				stub = server_pb2_grpc.ServerStub(channel)
				response = stub.LeaveServer(server_pb2.ClientDetails(client_uuid=self.id))
				if(response.request_status == True):
					print("SUCCESS")
				else:
					print("FAILED")
		except Exception as e:
			print("Invalid address")
			return

	def GetArticles(self):
		addr = input("Address of server (ip:port) = ")
		tag = input("Article tag (sports, fashion, politics, else all): ").lower() 
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
		
		try:
			with grpc.insecure_channel(addr) as channel:
				stub = server_pb2_grpc.ServerStub(channel)
				response = stub.GetArticles(reqArticle)
		except Exception as e:
			print("Invalid address")
			return

		if(response.status == False):
			print("FAILED")
		else:
			# print articles
			for article in response.articles:
				artTag = "SPORTS" if (article.SPORTS) else "FASHION" if (article.FASHION) else "POLITICS"
				print(artTag)
				print(article.author)
				print(f"{article.day}/{article.month}/{article.year}")
				print(article.content)
				print()
		
	def PublishArticles(self):
		addr = input("Address of server (ip:port) = ")
		tag = input("Article tag (sports, fashion, politics): ").lower() 
		pubArticle = server_pb2.Article(client_uuid=self.id,day=1,month=1,year=1)
		if(tag == 'sports'):
			pubArticle.SPORTS = True
		elif(tag == 'fashion'):
			pubArticle.FASHION = True 
		elif(tag == 'politics'):
			pubArticle.POLITICS = True 
		else:
			print("Invalid Tag")
			return
		author = input("Enter author name: ")
		pubArticle.author = author
		content = input("Enter content: ")
		pubArticle.content = content

		with grpc.insecure_channel(addr) as channel:
			stub = server_pb2_grpc.ServerStub(channel)
			response = stub.PublishArticle(pubArticle)

		print(response.request_status)
		
if __name__== '__main__':
	client = Client()
	ch = 'x'
	registryChannel = grpc.insecure_channel(regServerAddr)
	registryStub = registryserver_pb2_grpc.RegistryServerStub(registryChannel)
	while(ch != 'q'):
		print("---------------####----------------")
		print("Get server list (g) | Join Server (j) | Get Article (a) | Publish (p) | Quit (q):")
		ch = input().lower()
		if(ch == 'q'):
			break 
		elif(ch == 'g'):
			client.GetServerList(registryStub)
		elif(ch == 'j'):
			client.JoinServer()
		elif(ch == 'a'):
			client.GetArticles()
		elif(ch == 'p'):
			client.PublishArticles()
		else:
			print("Invalid input")
		print("-----------------------------------")
	