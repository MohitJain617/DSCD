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

	def JoinServer(self, stub):
		pass
	def LeaveServer(self, stub):
		pass
	def GetArticles(self, stub):
		pass
	def PublishArticles(self, stub):
		pass
		