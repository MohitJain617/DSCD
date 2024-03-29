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
		
		with grpc.insecure_channel(addr) as channel:
			stub = server_pb2_grpc.ServerStub(channel)
			response = stub.GetArticles(reqArticle)

		if(response.status == False):
			print("FAILED")
		else:
			# print articles
			for article in response.articles:
				artTag = "SPORTS" if (article.SPORTS) else "FASHION" if (article.FASHION) else "POLITICS"
				print()
				print(artTag)
				print(article.author)
				print(f"{article.day}/{article.month}/{article.year}")
				print(article.content)
		
	def PublishArticle(self):
		addr = input("Address of server (ip:port) = ")
		tag = input("Article tag (sports, fashion, politics): ").lower() 
		author = input("Enter author name: ")
		content = input("Enter content: ")
		day = int(1)
		month = int(1)
		year = int(1)

		pubArticle = server_pb2.Article(author=author,content=content,day=day,month=month,year=year,client_uuid=self.id)
		if(tag == 'sports'):
			pubArticle.SPORTS = True
		elif(tag == 'fashion'):
			pubArticle.FASHION = True 
		elif(tag == 'politics'):
			pubArticle.POLITICS = True 
		else:
			print("Invalid Tag")
			return
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
		print("Get server list (g) | Join Server (j) | Leave Server (l) | Get Article (a) | Publish (p) | Quit (q):")
		ch = input().lower()
		if(ch == 'q'):
			break 
		elif(ch == 'g'):
			client.GetServerList(registryStub)
		elif(ch == 'j'):
			client.JoinServer()
		elif(ch == 'l'):
			client.LeaveServer()
		elif(ch == 'a'):
			client.GetArticles()
		elif(ch == 'p'):
			client.PublishArticle()
		else:
			print("Invalid input")
		print("-----------------------------------")
	