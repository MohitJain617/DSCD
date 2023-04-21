from concurrent import futures
import grpc
import mapper_pb2
import mapper_pb2_grpc
import time
import os
import sys

# create gRPC server
class Mapper(mapper_pb2_grpc.MapperServicer):
	def __init__(self, addr, port, name):
		self.addr = addr
		self.port = port
		self.dir_name = name

	def ProcessFiles(self, request, context):
		print("Map request received", self.dir_name)
		print(request)
		return mapper_pb2.ProcessFilesResponse(response=True)


if __name__ == '__main__':
	args = sys.argv
	port = str(args[1])
	name = str(args[2])

	obj = Mapper('localhost', port, name)
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	mapper_pb2_grpc.add_MapperServicer_to_server(obj, server)
	server.add_insecure_port('[::]:'+port)
	server.start()
	print(name, "Server started")
	time.sleep(300) # run for 5 mins
	print("server done")
	server.stop(0)
