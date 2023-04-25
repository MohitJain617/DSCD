from concurrent import futures
import grpc
import mapper_pb2
import mapper_pb2_grpc
import time
import os
import sys
import pickle


INPUT_DIR = "Data/Inputs"
MAPPER_DIR = "Data/Mappers"
COMMON_KEY = "name"

# create gRPC server
class Mapper(mapper_pb2_grpc.MapperServicer):
	def __init__(self, addr, port, name):
		self.addr = addr
		self.port = port
		self.dir_name = name
		self.curr_task = ""

	def ASCII_SUM(self, word) :
		val = 0
		for c in word :
			val += ord(c)
		return val

	def word_count_handler(self, input_files, N_Reducers = 3) :

		word_count = {}

		for file in input_files : 
			input_file_path = os.path.join(INPUT_DIR, self.curr_task, file)
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
		
		reducers_dicts = [{} for i in range(N_Reducers)]

		for word in word_count : 
			val = self.ASCII_SUM(word)
			reducers_dicts[val%N_Reducers][word] = str(word_count[word])

		for i in range(N_Reducers):
			out_file_path = os.path.join(os.path.join(MAPPER_DIR, self.dir_name), str(i+1) + '.txt')	
			
			str_dict = str(reducers_dicts[i]) 
			with open(out_file_path, "w") as f:
				f.write(str_dict)

			# with open(out_file_path, "w") as f:
			# 	pickle.dump(reducers_dicts[i], out_file_path)

		return True

	def inverted_index_handler(self, input_files, N_Reducers = 3) :

		inverted_index = {}
		for file_name in input_files : 
			count = int(file_name[-5])
			input_file_path = os.path.join(INPUT_DIR, self.curr_task, file_name)
			print("AAA", input_file_path)
			with open(input_file_path, 'r') as file :
				for line in file :
					if line[-1] == '\n' :
						line = line[:-1]
					words = line.split(' ')
					for word in words :
						word = word.lower()
						if(word in inverted_index and inverted_index[word][-1] != file_name):
							inverted_index[word].append(str(file_name))
						elif(word not in inverted_index) :
							inverted_index[word] = [str(file_name)]

		os.mkdir(os.path.join(MAPPER_DIR, self.dir_name))

		reducers_dict = [{} for i in range(N_Reducers)]


		for word in inverted_index : 
			val = self.ASCII_SUM(word)
			reducers_dict[val%N_Reducers][word] = inverted_index[word]

			# output = word + ' ' + str(", ".join(str(x) for x in inverted_index[word])) + '\n'
			# out_file_path = os.path.join(os.path.join(MAPPER_DIR, self.dir_name), str((val % N_Reducers) + 1) + '.txt')
			# with open(out_file_path, 'a+') as file:
			# 	file.write(output)

		for i in range(N_Reducers):
			out_file_path = os.path.join(os.path.join(MAPPER_DIR, self.dir_name), str(i+1) + '.txt')	
			
			str_dict = str(reducers_dict[i]) 
			with open(out_file_path, "w") as f:
				f.write(str_dict)

			# with open(out_file_path, "w") as f:
			# 	pickle.dump(reducers_dicts[i], out_file_path)
		

		return True
	# assumes each table only has 2 columns and one of them is common
	def natural_join_handler(self, input_files, N_Reducers) :
		# common_key: (table, (key, val))
		natural_join_dict = {}

		for file_name in input_files:
			table_name = file_name.split("_")[-1].split(".")[0]
			input_file_path = os.path.join(INPUT_DIR, self.curr_task, file_name)
			common_key_id = 0
			unique_key_id = 1
			with open(input_file_path, "r") as f:
				lines = f.readlines()
				for i in range(len(lines)):
					line = lines[i]
					if len(line) > 0 and line[0] == "\n":
						lines[i] = line[:-1]
			
				if len(lines) < 2:
					continue

				if lines[0].split(",")[0].strip().lower() == COMMON_KEY.lower():
					common_key_id = 0
					unique_key_id = 1
				else: 
					common_key_id = 1
					unique_key_id = 0

				unique_key_label = lines[0].split(",")[unique_key_id].strip().lower()
				for i in range(1, len(lines)):
					common_key_val = lines[i].split(",")[common_key_id].strip()
					unique_key_val = lines[i].split(",")[unique_key_id].strip()
					if common_key_val in natural_join_dict:
						natural_join_dict[common_key_val].append((table_name, (unique_key_label, unique_key_val)))
					else:
						natural_join_dict[common_key_val] = [(table_name, (unique_key_label, unique_key_val))]
			
		reducers_dict = [{} for i in range(N_Reducers)]
		for common_val, uni_list in natural_join_dict.items():
			val = self.ASCII_SUM(common_val)
			reducers_dict[val%N_Reducers][common_val] = uni_list
		
		# print("RED:", len(reducers_dict[0]), len(reducers_dict[1]))

		os.mkdir(os.path.join(MAPPER_DIR, self.dir_name))

		for i in range(N_Reducers):
			
			out_file_path = os.path.join(os.path.join(MAPPER_DIR, self.dir_name), str(i+1) + '.txt')	
			
			str_dict = str(reducers_dict[i]) 
			with open(out_file_path, "w") as f:
				f.write(str_dict)	

		return True

	def helper(self, input_files, task, n_reducers) :
		self.curr_task = task.lower()
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
		curr_file = os.path.join(MAPPER_DIR, self.dir_name, str(curr_id) + '.txt')
		if(not os.path.exists(curr_file)):
			return mapper_pb2.KV(dict_object = "{}")
		with open(curr_file, "rb") as f:
			curr_dict = f.read() 
		return mapper_pb2.KV(dict_object = curr_dict)


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
	time.sleep(30) # run for 5 mins
	print("Mapper done")
	server.stop(0)
