from concurrent import futures
import grpc
import reducer_pb2
import reducer_pb2_grpc
import time
import os
import sys


INPUT_DIR = "Data/Inputs"
MAPPER_DIR = "Data/Reducers"

# create gRPC server
class Reducer(reducer_pb2_grpc.ReducerServicer):
	def __init__(self, addr, port, curr_id):
		self.addr = addr
		self.port = port
		self.id = curr_id


	def ProcessFiles(self, request, context):
		self.id = request.id
		print("Reduce request received", self.id)
		return reducer_pb2.ProcessFilesResponse(response=True)


if __name__ == '__main__':
	args = sys.argv
	port = str(args[1])
	curr_id = str(args[2])

	obj = Reducer('localhost', port, curr_id)
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	reducer_pb2_grpc.add_ReducerServicer_to_server(obj, server)
	server.add_insecure_port('[::]:'+port)
	server.start()
	print(curr_id, "Reducer started")
	time.sleep(300) # run for 5 mins
	print(curr_id, "Reducer stopping.")
	server.stop(0)

