from concurrent import futures 
import grpc
import registryserver_pb2
import registryserver_pb2_grpc
import replica_pb2
import replica_pb2_grpc


class RegistryServer(registryserver_pb2_grpc.RegistryServerServicer):
	def __init__(self) -> None:
		super().__init__()
		self.primary_replica = None
		self.replicalist = []
		# to connect with the primary stub
		self.prStub = None

	def RegisterReplica(self, request, context):
		print(f"REPLICA live request: {request.name} -> {request.addr}")

		if(self.primary_replica == None):
			self.primary_replica = request
			self.prStub = replica_pb2_grpc.ReplicaStub(grpc.insecure_channel(self.primary_replica.addr))

		else:
			response = self.prStub.UpdateReplicaList(replica_pb2.ReplicaDetails(name=request.name,addr=request.addr))
			if(response.status == False):
				print("Failed to update replica list")
			else:
				print("Successfully updated replica list")

		self.replicalist.append(request)

		# print details of all replicas
		for replica in self.replicalist:
			print(replica.name + ". " + replica.addr)

		return self.primary_replica

	def GetReplicaList(self, request, context):
		print(f"SERVER LIST REQUEST FROM {request.client_uuid}")
		rlist = registryserver_pb2.ReplicaList()
		rlist.replica_list.extend(self.replicas)
		return rlist
	
def serve():
	port = '50051'
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=12))
	registryserver_pb2_grpc.add_RegistryServerServicer_to_server(RegistryServer(), server)
	server.add_insecure_port('[::]:' + port)
	server.start()
	print("Registry Server started, listening on " + port)
	server.wait_for_termination()
 
if __name__ == '__main__':
    serve()