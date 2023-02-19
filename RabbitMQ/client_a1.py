#!/usr/bin/env python
import pika
import uuid
import server_pb2
import registryserver_pb2

class Client(object):
	def __init__(self) -> None:
		self.id = str(uuid.uuid4())
		self.server_list = []

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

		self.response = None
		self.corr_id = None

	def processResponse(self, ch, method, props, body):
		
		if props.type == "server-list":
			self.server_list = []
			result = registryserver_pb2.ServerList()
			result.ParseFromString(body)

			for server in result.server_list:
				self.server_list.append(server)
				print(f"{server.name} -> {server.addr}")

		elif props.type == "join-server":
			print(str(body))
		elif props.type == "leave-server":
			print(str(body))
		elif props.type == "get-articles":
			article_list = server_pb2.ArticleList()
			article_list.ParseFromString(body)

			if article_list.status == False:
				print("FAIL")
			else:
				article_list = server_pb2.ArticleList()
				article_list.ParseFromString(body)
				for article in article_list.articles:
					artTag = "SPORTS" if (article.SPORTS) else "FASHION" if (article.FASHION) else "POLITICS"
					print()
					print(artTag)
					print(article.author)
					print(f"{article.day}/{article.month}/{article.year}")
					print(article.content)
		
		elif props.type == "pub-article":
			print(str(body))


		

	def getServerList(self):
		self.response = None
		self.corr_id = str(uuid.uuid4())

		n = 1
		message = str(n)
		self.channel.basic_publish(
			exchange="",
			routing_key="register-server-rpc",
			properties=pika.BasicProperties(
				reply_to=self.callback_queue,
				correlation_id=self.id,
				type="server-list",
				# user_id=self.id,
				),
			body=message
		)

		self.connection.process_data_events(time_limit=None)

		return 0


	def joinServer(self):
		if len(self.server_list) == 0:
			print("No servers available")
			return
		for i in range(len(self.server_list)):
			print(f"ID: {i}")
			print(self.server_list[i])
			print("-----------------------------------")
		
		print("Enter the server ID you want to join: ")
		server_id = int(input())

		server_detail = server_pb2.ClientDetails()
		server_detail.client_uuid = self.id
		message = server_detail.SerializeToString()

		self.channel.basic_publish(
			exchange="",
			routing_key=self.server_list[server_id].addr,
			properties=pika.BasicProperties(
				reply_to=self.callback_queue,
				correlation_id=self.id,
				type="join-server",
				# user_id=self.id,
				),
			body=message
		)

		self.connection.process_data_events(time_limit=None)


	def leaveServer(self):
		if len(self.server_list) == 0:
			print("No servers available")
			return
		for i in range(len(self.server_list)):
			print(f"ID: {i}")
			print(self.server_list[i])
			print("-----------------------------------")
		
		print("Enter the server ID you want to leave: ")
		server_id = int(input())

		server_detail = server_pb2.ClientDetails()
		server_detail.client_uuid = self.id
		message = server_detail.SerializeToString()

		self.channel.basic_publish(
			exchange="",
			routing_key=self.server_list[server_id].addr,
			properties=pika.BasicProperties(
				reply_to=self.callback_queue,
				correlation_id=self.id,
				type="leave-server",
				# user_id=self.id,
				),
			body=message
		)

		self.connection.process_data_events(time_limit=None)


	def getArticles(self):		
		if len(self.server_list) == 0:
			print("No servers available")
			return
		for i in range(len(self.server_list)):
			print(f"ID: {i}")
			print(self.server_list[i])
			print("-----------------------------------")
		
		print("Enter the server ID you want to get article from: ")
		server_id = int(input())


		tag = input("Article tag (sports, fashion, politics, else all): ").lower() 
		# tag
		req_article = server_pb2.RequestMessage(client_uuid=self.id)
		if(tag == 'sports'):
			req_article.SPORTS = True
		elif(tag == 'fashion'):
			req_article.FASHION = True 
		elif(tag == 'politics'):
			req_article.POLITICS = True 
		else:
			req_article.allTags = True
		# author 
		author = input("Author name (or blank):")
		req_article.author = author
		# date 
		day = int(input("day: "))
		month = int(input("month: "))
		year = int(input("year: "))
		req_article.day = day
		req_article.month = month
		req_article.year = year

		# Send Request

		message = req_article.SerializeToString()

		self.channel.basic_publish(
			exchange="",
			routing_key=self.server_list[server_id].addr,
			properties=pika.BasicProperties(
				reply_to=self.callback_queue,
				correlation_id=self.id,
				type="get-articles",
				# user_id=self.id,
				),
			body=message
		)

		self.connection.process_data_events(time_limit=None)


	def publishArticle(self):
		if len(self.server_list) == 0:
			print("No servers available")
			return
		# print("Se")
		for i in range(len(self.server_list)):
			print(f"ID: {i}")
			print(self.server_list[i])
			print("-----------------------------------")
		
		print("Enter the server ID you want to publish to: ")
		server_id = int(input())


		tag = input("Article tag (sports, fashion, politics): ").lower() 
		author = input("Enter author name: ")
		content = input("Enter content: ")
		day = int(1)
		month = int(1)
		year = int(1)

		pub_article = server_pb2.Article(author=author,content=content,day=day,month=month,year=year,client_uuid=self.id)
		if(tag == 'sports'):
			pub_article.SPORTS = True
		elif(tag == 'fashion'):
			pub_article.FASHION = True 
		elif(tag == 'politics'):
			pub_article.POLITICS = True 
		else:
			print("Invalid Tag")
			return


		# Call RPC
		message = pub_article.SerializeToString()

		self.channel.basic_publish(
			exchange="",
			routing_key=self.server_list[server_id].addr,
			properties=pika.BasicProperties(
				reply_to=self.callback_queue,
				correlation_id=self.id,
				type="pub-article",
				# user_id=self.id,
				),
			body=message
		)

		self.connection.process_data_events(time_limit=None)

	

if __name__== '__main__':
	client = Client()
	ch = 'x'
	while(ch != 'q'):
		print("---------------####----------------")
		print("Get server list (g) | Join Server (j) | Leave Server (h) | Get Article (a) | Publish (p) | Quit (q):")
		ch = input().lower()
		if(ch == 'q'):
			break 
		elif(ch == 'g'):
			client.getServerList()
		elif(ch == 'j'):
			client.joinServer()
		elif(ch == 'h'):
			client.leaveServer()
		elif(ch == 'a'):
			client.getArticles()
		elif(ch == 'p'):
			client.publishArticle()
		else:
			print("Invalid input")
		print("-----------------------------------")
	