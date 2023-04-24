from concurrent import futures
import grpc
import mapper_pb2
import mapper_pb2_grpc
import time
import os
import sys


INPUT_DIR = "Data/Inputs"
MAPPER_DIR = "Data/Mappers"

# create gRPC server
class Mapper(mapper_pb2_grpc.MapperServicer):
	def __init__(self, addr, port, name):
		self.addr = addr
		self.port = port
		self.dir_name = name

	def ASCII_SUM(self, word) :
		val = 0
		for c in word :
			val += ord(c)
		return val

	def word_count_handler(self, input_files, N_Reducers = 3) :

		word_count = {}

		for file in input_files : 
			input_file_path = os.path.join(INPUT_DIR, file)
			with open(input_file_path, 'r') as file :
				for line in file :
					if line[-1] == '\n' :
						line = line[:-1]
					words = line.split(' ')
					for word in words :
						word = word.lower()
						if(word in word_count):
							word_count[word] += 1
						else :
							word_count[word] = 1 

		print("Word count: ", word_count, self.dir_name)
		os.mkdir(os.path.join(MAPPER_DIR, self.dir_name))

		for word in word_count : 
			val = self.ASCII_SUM(word)
			output = word + ' ' + str(word_count[word]) + '\n'
			out_file_path = os.path.join(os.path.join(MAPPER_DIR, self.dir_name), str((val % N_Reducers) + 1) + '.txt')
			with open(out_file_path, 'a+') as file:
				file.write(output)

		return True

	def inverted_index_handler(self, input_files, N_Reducers = 3) :

		inverted_index = {}
		for file in input_files : 
			count = int(file[-5])
			input_file_path = os.path.join(INPUT_DIR, file)
			with open(input_file_path, 'r') as file :
				for line in file :
					if line[-1] == '\n' :
						line = line[:-1]
					words = line.split(' ')
					for word in words :
						word = word.lower()
						if(word in inverted_index and inverted_index[word][-1] != count):
							inverted_index[word].append(count)
						elif(word not in inverted_index) :
							inverted_index[word] = [count]

		os.mkdir(os.path.join(MAPPER_DIR, self.dir_name))

		for word in inverted_index : 
			val = self.ASCII_SUM(word)
			output = word + ' ' + str(", ".join(str(x) for x in inverted_index[word])) + '\n'
			out_file_path = os.path.join(os.path.join(MAPPER_DIR, self.dir_name), str((val % N_Reducers) + 1) + '.txt')
			with open(out_file_path, 'a+') as file:
				file.write(output)

		return True

	def natural_join_handler(self, input_files, N_Reducers) :
		return True

	def helper(self, input_files, task, n_reducers) :
		
		if(task == 'WORD COUNT') :
			print("Helper called with ", input_files)
			return self.word_count_handler(input_files, n_reducers)
		
		elif(task == 'INVERTED INDEX') :
			return self.inverted_index_handler(input_files, n_reducers)

		elif(task == 'NATURAL JOIN') :
			return self.natural_join_handler(input_files, n_reducers)

		else :
			return False

	def ProcessFiles(self, request, context):
		print("Map request received", self.dir_name)
		file_names = [elem for elem in request.filenames]
		print(file_names)
		verdict = self.helper(file_names, request.task, request.num_reducers )
		print(verdict)
		return mapper_pb2.ProcessFilesResponse(response=verdict)
	
	def ReturnKV(self, request, context):
		curr_id = request.id
		
		return mapper_pb2.KV(dict_object=)


if __name__ == '__main__':
	args = sys.argv
	port = str(args[1])
	name = str(args[2])

	obj = Mapper('localhost', port, name)
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	mapper_pb2_grpc.add_MapperServicer_to_server(obj, server)
	server.add_insecure_port('[::]:'+port)
	server.start()
	print(name, "Mapper started")
	time.sleep(300) # run for 5 mins
	print("Mapper done")
	server.stop(0)
