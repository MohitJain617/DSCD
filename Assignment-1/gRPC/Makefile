all: command1 command2

command1:
	python -m grpc_tools.protoc -I../protos --python_out=. --pyi_out=. --grpc_python_out=. ../protos/registryserver.proto

command2:
	python -m grpc_tools.protoc -I../protos --python_out=. --pyi_out=. --grpc_python_out=. ../protos/server.proto

clean:
	rm server_pb2_grpc.py server_pb2.py server_pb2.pyi registryserver_pb2_grpc.py registryserver_pb2.py registryserver_pb2.pyi