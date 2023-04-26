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
COMMON_KEY = "name"

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
		if request.task == "WORD COUNT":
			self.word_count_handler(dict_list)
		elif request.task == "INVERTED INDEX":
			self.inverted_index_handler(dict_list)
		elif request.task == "NATURAL JOIN":
			self.natural_join_handler(dict_list)
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


	def natural_join_handler(self, mapper_dicts: list):
		final_joined_table = []
		tables = []
		table_ids = {}
		available_id = 0
		pretty_out = ""


		for map_dict in mapper_dicts:
			for common_val, unique_val_list in map_dict.items():
				for unique_val in unique_val_list:
					if unique_val[0] not in table_ids:
						table_ids[unique_val[0]] = available_id
						tables.append({})
						available_id += 1
					table_id = table_ids[unique_val[0]] 

					if common_val not in tables[table_id]:
						tables[table_id][common_val] = [unique_val[1]]
					else:
						tables[table_id][common_val].append(unique_val[1])
		

		
		for i in range(len(tables)):
			for common_val, unique_val_list in tables[i].items():
				for unique_val_1 in unique_val_list:
					for j in range(i+1, len(tables)):
						if common_val in tables[j]:
							unique_val_list_2 = tables[j][common_val]
							for unique_val_2 in unique_val_list_2:
								# row = COMMON_KEY + " = " + common_val + ", " + str(unique_val_1) + " " + str(unique_val_2)
								row = "{} = {}, {} = {}, {} = {}".format(COMMON_KEY, common_val, unique_val_1[0], unique_val_1[1], unique_val_2[0], unique_val_2[1])
								final_joined_table.append(row)
								pretty_out += row + "\n"

		



		
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
	time.sleep(30) # run for 5 mins
	print(curr_id, "Reducer stopping.")
	server.stop(0)

