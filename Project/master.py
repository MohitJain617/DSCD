from multiprocessing import Pool, Manager
import os
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
	ports = arglist[0:-3]
	inp_task = arglist[-3]
	port = arglist[-2]
	r_id = arglist[-1]

	subprocess.Popen(["python3", "reduces.py", port, r_id])
	time.sleep(1)
	processFiles = reducer_pb2.ProcessFilesRequest(task=inp_task)
	processFiles.ports.extend(ports)

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
	datamdir = os.path.join(os.getcwd(), "Data", "Mappers")
	datardir = os.path.join(os.getcwd(), "Data", "Reducers")
	subprocess.call(["rm", "-rf", datamdir])
	subprocess.call(["mkdir", datamdir])
	subprocess.call(["rm", "-rf", datardir])
	subprocess.call(["mkdir", datardir])

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
	portslist = []
	for i in range(len(processDetailsList)):
		processDetailsList[i].extend([inp_task, str(num_reducers), str(port), "M"+str(i+1)])
		processDetailsList[i] = repr(processDetailsList[i])
		portslist.append(str(port))
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
		processDetailsList.append(portslist + [inp_task, str(port), str(i+1)])
		processDetailsList[i] = repr(processDetailsList[i])
		port += 1
	
	print()

	# execute_reducer(processDetailsList[0])

	with Pool() as pool:
		result = pool.map_async(execute_reducer, processDetailsList)
		result.wait()
	
	print("All reducers done")
	
