Implemented a pubsub (like a Discord) Model using ZeroMQ (REQ-REP Sockets) and google protocal buffers.

Running Instructions
--------------------
1. Proto file to describe the structure of messages
2. Generate _pb2.py files (protoc registryserver.proto --python_out='.' & protoc server.proto --python_out='.')
3. Run registryserver.py (Only once)
4. Run server_a1.py (Can start multiple servers on different terminals/addresses)
5. Run client_a1.py (Can start multiple clients)

Explore various functions of client.

- Error handling : Socket timeout : 10s, Valid Addresses, Valid Dates, etc.

Registry Server Address Used : localhost:5555



Resources
----------
- https://zeromq.org/languages/python/
- https://github.com/protocolbuffers/protobuf/tree/main/examples
- https://osdevlab.blogspot.com/2016/03/send-google-protocol-buffer-with-zeromq.html
- https://github.com/junhyeokahn/zmq-protobuf/tree/master/py-py

