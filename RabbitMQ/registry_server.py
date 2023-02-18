#!/usr/bin/env python
import pika
import registryserver_pb2

MAXSERVERS = 10

class RegistryServer(object):
	
	def __init__(self):
		self.name = "reg-server"
		self.registered_servers = []

		self.connection = pika.BlockingConnection(
			pika.ConnectionParameters(
				host="localhost"
				# heartbeat=600
			)
		)

		self.channel = self.connection.channel()
		result = self.channel.queue_declare(queue="register-server-rpc")
		self.channel.basic_qos(prefetch_count=1)
		self.channel.basic_consume(queue="register-server-rpc", on_message_callback=self.handleRpc)
		print("Waiting for RPCs")
		self.channel.start_consuming()

		# self.initRegisterRpc()
		# self.initGetServerRpc()
		print("done")

	def register(self, body):
		server_detail = registryserver_pb2.ServerDetails()
		server_detail.ParseFromString(body)

		print(f"JOIN REQUEST FROM {server_detail.name} -> {server_detail.addr}")
		if len(self.registered_servers) >= MAXSERVERS:
			return "FAIL"

		self.registered_servers.append(server_detail)
		return "SUCCESS"

	def getServerList(self):
		server_list = registryserver_pb2.ServerList()
		server_list.server_list.extend(self.registered_servers)
		print(server_list)
		return server_list.SerializeToString()


	def handleRpc(self, ch, method, props, body):
		print("Hello")
		if props.type == "register":
			print("register called")
			response = self.register(body)
		elif props.type == "server-list":
			print(f"server list requested from {props.correlation_id}")
			response = self.getServerList()
		else:
			print("Unrecognised RPC request")


		ch.basic_publish(
			exchange='',
			routing_key=props.reply_to,
			properties=pika.BasicProperties(type=props.type),
			body=response
		)

		ch.basic_ack(delivery_tag=method.delivery_tag)

test_server = RegistryServer()
