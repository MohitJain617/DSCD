from multiprocessing import Pool, Manager
import time
import subprocess
import glob
import grpc
import mapper_pb2
import mapper_pb2_grpc
import reducer_pb2
import reducer_pb2_grpc
from ast import literal_eval

def execute_mapper(arg):
	arglist = literal_eval(arg)
	filenames = arglist[0:-4]
	inp_task = arglist[-4]
	num_reducers = arglist[-3]
	port = arglist[-2]
	name = arglist[-1]

	subprocess.Popen(["python3", "maps.py", port, name])
	time.sleep(1)
	processFiles = mapper_pb2.ProcessFilesRequest(num_reducers=int(num_reducers), task=inp_task)
	print("Sending gRPC call to", name)
	for filename in filenames:
		processFiles.filenames.append(filename)
	with grpc.insecure_channel('localhost:'+port) as channel:
		stub = mapper_pb2_grpc.MapperStub(channel)
		response = stub.ProcessFiles(processFiles)
		if(response.response == False):
			print("Error in mapper", name)
	
	print("Mapped for", name) 

def execute_reducer(arg):
	arglist = literal_eval(arg)
	filename = arglist[0]
	inp_task = arglist[1]
	port = arglist[2]
	r_id = arglist[3]

	subprocess.Popen(["python3", "reduces.py", port, r_id])
	time.sleep(1)
	processFiles = reducer_pb2.ProcessFilesRequest(id=filename, task=inp_task)
	with grpc.insecure_channel('localhost:'+port) as channel:
		stub = reducer_pb2_grpc.ReducerStub(channel)
		response = stub.ProcessFiles(processFiles)
		if(response.response == False):
			print("Error in reducer", r_id)
	print("Reduced for", r_id)
	


if __name__ == '__main__':
	num_mappers = int(input("Enter number of mappers: "))
	num_reducers = int(input("Enter number of reducers: "))
	inp_task = input("Enter task: ")

	# Clear output directory
	subprocess.call(["rm", "-rf", "Data/Mappers"])
	subprocess.call(["mkdir", "Data/Mappers"])
	subprocess.call(["rm", "-rf", "Data/Reducers"])
	subprocess.call(["mkdir", "Data/Reducers"])

	# read all file names:
	file_names = glob.glob("Data/Inputs/*")
	file_names.sort()

	processDetailsList = []

	# Create a list of ProcessFilesRequest objects
	for i in range(num_mappers):
		processDetailsList.append([])

	# Distribute files among mappers
	for i in range(len(file_names)):
		processDetailsList[i % num_mappers].append(file_names[i][12:])
	
	# Assign ports and names to mappers
	port = 50052
	for i in range(len(processDetailsList)):
		processDetailsList[i].extend([inp_task, str(num_reducers), str(port), "M"+str(i+1)])
		processDetailsList[i] = repr(processDetailsList[i])
		port += 1
	
		
	# Executing mappers in parallel
	# execute_mapper(processDetailsList[0])
	with Pool() as pool:
		result = pool.map_async(execute_mapper, processDetailsList)
		result.wait()
		
	print("All mappers done")
	
	# Executing reducers
	processDetailsList = []

	for i in range(num_reducers):
		processDetailsList.append([str(i+1), inp_task, str(port), str(i+1)])
		processDetailsList[i] = repr(processDetailsList[i])
		port += 1
	
	print()
	print()
	print()
	with Pool() as pool:
		result = pool.map_async(execute_reducer, processDetailsList)
		result.wait()
	
	print("All reducers done")
	
