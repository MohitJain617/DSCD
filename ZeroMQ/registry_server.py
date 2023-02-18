import time
import zmq
import registryserver_pb2

MAXSERVERS = 10
PORT = 5555

class RegistryServer():

    def __init__(self):
        self.servers = []

    def HandleRequest(self,message) :
        request = registryserver_pb2.RegistryServerMessage()
        request.ParseFromString(message)

        if request.WhichOneof('Details') == 'clientDetails':
            clientDetails = registryserver_pb2.ClientDetails()
            clientDetails = request.clientDetails
            serverList = self.GetServerList(clientDetails).SerializeToString()
            return serverList
        
        elif request.WhichOneof('Details') == 'serverDetails':
            serverDetails = registryserver_pb2.ServerDetails()
            serverDetails = request.serverDetails
            status = self.Register(serverDetails).SerializeToString()
            return status

            
    def Register(self, request):
        print(f"JOIN REQUEST FROM {request.name} -> {request.addr}")
        if(len(self.servers) < MAXSERVERS):	
            self.servers.append(request)
            return registryserver_pb2.StatusOfRegistry(connected=True)
        else :
            return registryserver_pb2.StatusOfRegistry(connected=False)
	
    def GetServerList(self, request):
        print(f"SERVER LIST REQUEST FROM {request.client_uuid}")
        slist = registryserver_pb2.ServerList()
        slist.server_list.extend(self.servers)
        return slist
	
def serve():

    registryserver = RegistryServer()

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:" + str(PORT))

    while True :

        print('\nRegistry server listening for incoming requests...\n')
        
        #  Wait for next request from client
        request = socket.recv()
        
        # Check which type of request and handles it accordingly, returns protobuf after Serializing to string
        reply = registryserver.HandleRequest(request)

        # Send the reply 
        socket.send(reply)
 
if __name__ == '__main__':
    serve()