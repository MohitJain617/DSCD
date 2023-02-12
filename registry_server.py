from concurrent import futures 

import grpc
import registryserver_pb2
import registryserver_pb2_grpc

MAXSERVERS = 10

class RegistryServer(registryserver_pb2_grpc.RegistryServerServicer):
	def __init__(self) -> None:
		super().__init__()
		self.servers = []

	def Register(self, request, context):
		print(f"JOIN REQUEST FROM {request.name}:{request.addr}")
		if(len(self.servers) < MAXSERVERS):	
			self.servers.append(request)
			return registryserver_pb2.StatusOfRegistry(connected=True)
		else :
			return registryserver_pb2.StatusOfRegistry(connected=False)
	
	def GetServerList(self, request, context):
		print(f"SERVER LIST REQUEST FROM {request.client_uuid}")
		slist = registryserver_pb2.ServerList()
		slist.server_list.extend(self.servers)
		return slist
	
