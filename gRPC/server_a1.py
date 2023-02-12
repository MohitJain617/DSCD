from concurrent import futures 

import grpc
import registryserver_pb2
import registryserver_pb2_grpc
import server_pb2
import server_pb2_grpc

MAXCLIENTS = 200

class Server(server_pb2_grpc.ServerServicer):
	def __init__(self, name, ip, port) -> None:
		super().__init__()
		self.connected = False
		self.name = name
		self.ip = ip
		self.port = port
		self.clientelle = []
	
	def RegisterAsServer(self, stub):
		response = stub.Register(registryserver_pb2.ServerDetails(name=self.name,addr=f"{self.ip}:{self.port}"))
		self.connected = response.connected
		print(self.connected)
	
	def JoinServer(self, request, context):
		print(f"JOIN REQUEST FROM {request.client_uuid}")
		if(len(self.clientelle) >= MAXCLIENTS):
			return server_pb2.StatusOfClientRequest(request_status=False)
		self.clientelle.append(request)
		return server_pb2.StatusOfClientRequest(request_status=True)
	
	def LeaveServer(self, request, context):
		print(f"LEAVE REQUEST FROM {request.client_uuid}")
		prevlen = len(self.clientelle)
		self.clientelle[:] = (client for client in self.clientelle if (client.client_uuid != request.client_uuid))
		newlen = len(self.clientelle)
		return server_pb2.StatusOfClientRequest(request_status= (prevlen > newlen))

	def GetArticles(self, request, context):
		return super().GetArticles(request, context)
	
	def PublishArticle(self, request, context):
		return super().PublishArticle(request, context)
	