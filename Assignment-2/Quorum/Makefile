all: command1 command2

command1:
	python3 -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/registryserver.proto

command2:
	python3 -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/replica.proto

clean:
	rm replica_pb2_grpc.py replica_pb2.py replica_pb2.pyi registryserver_pb2_grpc.py registryserver_pb2.py registryserver_pb2.pyi