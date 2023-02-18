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
		print("HHH")
		if props.type == "server-list":
			self.server_list = []
			result = registryserver_pb2.ServerList()
			result.ParseFromString(body)

			for server in result.server_list:
				self.server_list.append(server)
				print(f"{server.name} -> {server.addr}")

			print("got it!")

		

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

test_client = Client()

# print(test_client.getServerList())

# test_client.getServerList()
# test_client.getServerList()
# test_client.getServerList()

# while True:
# 	test_client.getServerList()
# 	a = 1

if __name__== '__main__':
	client = Client()
	ch = 'x'
	while(ch != 'q'):
		print("---------------####----------------")
		print("Get server list (g) | Join Server (j) | Get Article (a) | Publish (p) | Quit (q):")
		ch = input().lower()
		if(ch == 'q'):
			break 
		elif(ch == 'g'):
			client.getServerList()
		elif(ch == 'j'):
			client.joinServer()
		elif(ch == 'a'):
			client.getArticles()
		elif(ch == 'p'):
			client.publishArticle()
		else:
			print("Invalid input")
		print("-----------------------------------")
	