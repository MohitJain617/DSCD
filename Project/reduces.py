from concurrent import futures
import grpc
import reducer_pb2
import reducer_pb2_grpc
import mapper_pb2
import mapper_pb2_grpc
import time
import os
import sys


INPUT_DIR = "Data/Inputs"
REDUCER_DIR = "Data/Reducers"

# create gRPC server
class Reducer(reducer_pb2_grpc.ReducerServicer):
	def __init__(self, addr, port, curr_id):
		self.addr = addr
		self.port = port
		self.id = curr_id
		self.dir_name = str(self.id)


	def ProcessFiles(self, request: reducer_pb2.ProcessFilesRequest, context):
		print("Reduce request received", self.id)
		dict_list = []
		for port in request.ports:
			with grpc.insecure_channel('localhost:'+port) as channel:
				stub = mapper_pb2_grpc.MapperStub(channel)
				response = stub.ReturnKV(mapper_pb2.ReducerID(id=int(self.id)))
				dict_list.append(eval(response.dict_object))
		
		print(dict_list)
		print("HAAAAA" , request.task)
		if request.task == "WORD COUNT":
			self.word_count_handler(dict_list)
		elif request.task == "INVERTED INDEX":
			self.inverted_index_handler(dict_list)
		# elif request.task == "NATURAL JOIN":
			# self.
		return reducer_pb2.ProcessFilesResponse(response=True)


	def word_count_handler(self, mapper_dicts: list):
		final_word_count = {}

		for map_dict in mapper_dicts:
			for word, count in map_dict.items():
				if word not in final_word_count:
					final_word_count[word] = int(count)
				else: 
					final_word_count[word] += int(count)
		

		pretty_out = ""

		for word, count in final_word_count.items():
			pretty_out += word + " " + str(count) + "\n"
		
		
		out_path = os.path.join(REDUCER_DIR, self.dir_name + ".txt")

		with open(out_path, "w") as f:
			f.write(pretty_out)

		return True
	
	def inverted_index_handler(self, mapper_dicts: list):
		final_inverted_index = {} 

		for map_dict in mapper_dicts:
			for word, file in map_dict.items():
				if word not in final_inverted_index:
					final_inverted_index[word] = [file]
				elif file not in final_inverted_index[word]: 
					final_inverted_index[word].append(file)
		

		pretty_out = ""

		for word, files in final_inverted_index.items():
			pretty_out += word + " : " + str(files) + "\n"

		
		out_path = os.path.join(REDUCER_DIR, self.dir_name + ".txt")

		with open(out_path, "w") as f:
			f.write(pretty_out)

		return True


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

