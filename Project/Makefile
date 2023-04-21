all: command1 command2

command1:
	python3 -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/mapper.proto

command2:
	python3 -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/reducer.proto

clean:
	rm reducer_pb2_grpc.py reducer_pb2.py reducer_pb2.pyi mapper_pb2_grpc.py mapper_pb2.py mapper_pb2.pyi