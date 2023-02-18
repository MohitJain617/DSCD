#!/usr/bin/env python
import pika
import uuid
import server_pb2


class Server(object):
	def __init__(self) -> None:
		self.id = str(uuid.uuid4())

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

	
	def handleRpc(self, ch, method, props, body):
		print("Hello")
		if props.type == "register":
			print("register called")
		elif props.type == "server-list":
			print(f"server list requested from {props.user_id}")

		response = "hii"

		ch.basic_publish(
			exchange='',
			routing_key=props.reply_to,
			properties=pika.BasicProperties(type=props.type),
			body=str(response)
		)

		ch.basic_ack(delivery_tag=method.delivery_tag)
		

# message ServerDetails {
#   string name = 1;
#   string addr = 2;
# }

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