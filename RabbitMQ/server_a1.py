#!/usr/bin/env python
import pika
import uuid
import server_pb2
from datetime import date
from datetime import datetime

MAXCLIENTS = 10


def isValidDate(date_str, format_str='%d %m %Y'):
	try:
		datetime.strptime(date_str, format_str)
		return True
	except ValueError:
		print("VAL")
		print(date_str)
		return False

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

class Server(object):
	def __init__(self) -> None:
		self.id = str(uuid.uuid4())
		self.CLIENTELE = []
		self.articles = []
		self.connection = pika.BlockingConnection(
			pika.ConnectionParameters(host="localhost")
		)

		self.channel = self.connection.channel()
		result = self.channel.queue_declare(queue="", exclusive=True)
		self.callback_queue = result.method.queue

		self.channel.basic_consume(
			queue=self.callback_queue,
			on_message_callback=self.processResponse,
			auto_ack=True
		)
		
		self.registerAsServer()
		# server registered
		# start listening
		print("server registered!")


		result = self.channel.queue_declare(queue=self.id, exclusive=True)
		self.channel.basic_qos(prefetch_count=1)
		self.channel.basic_consume(queue=self.id, on_message_callback=self.handleRpc)
		print("Waiting for RPCs")
		self.channel.start_consuming()


	def processResponse(self, ch, method, props, body):
		if props.type == "register":
			print(str(body))
			# print("success!")
		if props.type == "server-list":
			print("got it!")

	def joinServer(self, body):
		if len(self.CLIENTELE) >= MAXCLIENTS:
			return str("FAIL")
		
		client_detail = server_pb2.ClientDetails()
		client_detail.ParseFromString(body)

		self.CLIENTELE.append(client_detail.client_uuid)

		return str("SUCCESS")

	def leaveServer(self, body):
		
		client_detail = server_pb2.ClientDetails()
		client_detail.ParseFromString(body)
		
		if client_detail.client_uuid in self.CLIENTELE:		
			self.CLIENTELE = [client for client in self.CLIENTELE if client != client_detail.client_uuid]
			return str("SUCCESS")
		else:
			return str("FAIL")

	def getArticles(self, body):
		request = server_pb2.Article()
		request.ParseFromString(body) 

		print(request)

		response = server_pb2.ArticleList()
		if (request.client_uuid not in self.CLIENTELE) or not (isValidDate(f"{request.day} {request.month} {request.year}")):
			print(request.client_uuid not in self.CLIENTELE)
			print(isValidDate(f"{request.day} {request.month} {request.year}"))
			response.status = False
		else:
			response.status = True

			for article in self.articles:
				if articleMatches(body, article):
					response.articles.append(article)

		return response.SerializeToString()

	def publishArticle(self, body):
		request = server_pb2.Article()
		request.ParseFromString(body) 

		if (request.client_uuid not in self.CLIENTELE):
			return str("FAIL")

		print(f"ARTICLES PUBLISH FROM {request.client_uuid}")
		request.year = date.today().year
		request.month = date.today().month
		request.day = date.today().day
		content = request.content 
		author = request.author 

		emptyTopic = (request.SPORTS==False and request.FASHION==False and request.POLITICS==False)
		if(content.strip() == "" or author.strip() == "" or emptyTopic or len(content) > 200):
			return str("FAIL")
	
		self.articles.append(request)
		print(request)
		return str("SUCCESS")

	
	def handleRpc(self, ch, method, props, body):
		print("Hello")
		if props.type == "join-server":
			print(f"Join request from {props.correlation_id}")
			response = self.joinServer(body)
		elif props.type == "leave-server":
			print(f"leave server requested from {props.correlation_id}")
			response = self.leaveServer(body)
		elif props.type == "get-articles":
			print(f"get article requested from {props.correlation_id}")
			response = self.getArticles(body)
		elif props.type == "pub-article":
			print(f"pub article requested from {props.correlation_id}")
			response = self.publishArticle(body)

		


		ch.basic_publish(
			exchange='',
			routing_key=props.reply_to,
			properties=pika.BasicProperties(type=props.type),
			body=response
		)

		ch.basic_ack(delivery_tag=method.delivery_tag)
		

	def registerAsServer(self):
		server_details = server_pb2.ServerDetails()
		server_details.name = "server a1"
		server_details.addr = self.id
		print(server_details)
		message = server_details.SerializeToString()

		self.response = None
		self.corr_id = str(uuid.uuid4())

		self.channel.basic_publish(
			exchange="",
			routing_key="register-server-rpc",
			properties=pika.BasicProperties(
				reply_to=self.callback_queue,
				correlation_id=self.corr_id,
				type="register",

				),
			body=message
		)

		self.connection.process_data_events(time_limit=None)

		return 0


test_server = Server()