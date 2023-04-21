from multiprocessing import Pool, Manager
import time
import subprocess
import glob
import grpc
import mapper_pb2
import mapper_pb2_grpc
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
		processDetailsList[i % num_mappers].append(file_names[i])
	
	# Assign ports and names to mappers
	port = 50052
	for i in range(len(processDetailsList)):
		processDetailsList[i].extend([inp_task, str(num_reducers), str(port), "M"+str(i+1)])
		port += 1
	
	for i in range(len(processDetailsList)):
		processDetailsList[i] = repr(processDetailsList[i])
		
	print(processDetailsList)
	# Executing mappers in parallel
	with Pool() as pool:
		pool.map(execute_mapper, processDetailsList)
	
