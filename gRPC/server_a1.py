from concurrent import futures 

import grpc
import registryserver_pb2
import registryserver_pb2_grpc
import server_pb2
import server_pb2_grpc
from datetime import date
from datetime import datetime

MAXCLIENTS = 200

def fibonacci(n):
    if(n < 3):
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def is_valid_date(date_str, format_str='%d %m %Y'):
	try:
		datetime.strptime(date_str, format_str)
		return True
	except ValueError:
		return False
    
class Server(server_pb2_grpc.ServerServicer):
	def __init__(self, name, ip, port) -> None:
		super().__init__()
		self.connected = False
		self.name = name
		self.ip = ip
		self.port = port
		self.clientelle = []     # list of string of clients uuid
		self.articles = []       # list server_pb2.Article 
	
	def RegisterAsServer(self, stub):
		response = stub.Register(registryserver_pb2.ServerDetails(name=self.name,addr=f"{self.ip}:{self.port}"))
		self.connected = response.connected
		print(self.connected)
	
	def JoinServer(self, request, context):
		print(f"JOIN REQUEST FROM {request.client_uuid}")
		if(len(self.clientelle) >= MAXCLIENTS):
			return server_pb2.StatusOfClientRequest(request_status=False)
		self.clientelle.append(request.client_uuid)
		return server_pb2.StatusOfClientRequest(request_status=True)
	
	def LeaveServer(self, request, context):
		print(f"LEAVE REQUEST FROM {request.client_uuid}")
		prevlen = len(self.clientelle)
		self.clientelle[:] = (client for client in self.clientelle if (client != request.client_uuid))
		newlen = len(self.clientelle)
		return server_pb2.StatusOfClientRequest(request_status= (prevlen > newlen))

	def articleMatches(request, article):
		# authors
		if(request.author != "" and request.author != article.author):
			return False
		# date check
		if(request.year > article.year):
			return False
		if(request.year == article.year and request.month > article.month):
			return False
		if(request.year == article.year and request.month == article.month and request.day > article.day):
			return False
		# check tag
		if(request.allTags == True):
			return True 
		if(request.SPORTS != article.SPORTS):
			return False
		if(request.FASHION != article.FASHION):
			return False
		if(request.POLITICS != article.POLITICS):
			return False
		
		return True

	def GetArticles(self, request, context):
		print(f"ARTICLE REQUEST FROM {request.client_uuid}")
		if(request.client_uuid not in self.clientelle):
			return server_pb2.ArticleList(status=False)
		matchedArticleList.fib = fibonacci(request.fibof)
		matchedArticleList = server_pb2.ArticleList(status=True)
		for article in self.articles:
			if(self.articleMatches(request, article)):
				matchedArticleList.articles.append(article)

		return matchedArticleList
	
	def PublishArticle(self, request, context):
		print(f"ARTICLES PUBLISH FROM {request.client.client_uuid}")
		request.year = date.today().year
		request.month = date.today().month
		request.day = date.today().day
		content = request.content 
		author = request.author 

		emptyTopic = (request.SPORTS==False and request.FASHION==False and request.POLITICS==False)
		if(content.strip() == "" or author.strip() == "" or emptyTopic or len(content) > 200):
			return server_pb2.StatusOfClientRequest(request_status=False)
	
		self.articles.append(request)
		return server_pb2.StatusOfClientRequest(request_status=True)
