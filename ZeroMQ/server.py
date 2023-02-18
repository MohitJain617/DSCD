import zmq
import registryserver_pb2
import server_pb2
from datetime import date
from datetime import datetime

MAXCLIENTS = 200
REGISTRY_SERVER_ADDR = 'localhost:5555'

def is_valid_date(date_str, format_str='%d %m %Y'):
	try:
		datetime.strptime(date_str, format_str)
		return True
	except ValueError:
		return False
    
def articleMatches(request, article):
	# authors
	if(request.author != "" and request.author != article.author):
		return False
	# date check
	if(request.year > article.year):
		return False
	if(request.year == article.year and request.month > article.month):
		return False
	if(request.year == article.year and request.month == article.month and request.day > article.day):
		return False
	# check tag
	if(request.allTags == True):
		return True 
	if(request.SPORTS != article.SPORTS):
		return False
	if(request.FASHION != article.FASHION):
		return False
	if(request.POLITICS != article.POLITICS):
		return False
	
	return True

class Server():
    
    def __init__(self, name, ip, port):
        self.connected = False
        self.name = name
        self.ip = ip
        self.port = port
        self.clientelle = []     # list of string of clients uuid
        self.articles = []       # list server_pb2.Article 

    def RegisterAsServer(self, socket):

        print("Connecting to Registry server…")
        socket.connect("tcp://"+REGISTRY_SERVER_ADDR)

        request = registryserver_pb2.RegistryServerMessage(serverDetails = registryserver_pb2.ServerDetails(name=self.name,addr=f"{self.ip}:{self.port}")).SerializeToString()
        socket.send(request)

        message = socket.recv()
        response = registryserver_pb2.StatusOfRegistry()
        response.ParseFromString(message)

        self.connected = response.connected

        if(self.connected) :
            print('SUCCESS')
        else :
            print('FAIL')

        return self.connected

    def HandleRequest(self,message) :
        
        request = server_pb2.ServerMessage()
        request.ParseFromString(message)

        if request.WhichOneof('Type') == 'clientDetails':
            clientDetails = server_pb2.ClientDetails()
            clientDetails = request.clientDetails

            if clientDetails.join == True :
                status = self.JoinServer(clientDetails).SerializeToString()
                return status
            elif clientDetails.leave == True :
                status = self.LeaveServer(clientDetails).SerializeToString()
                return status
            else :
                return server_pb2.StatusOfClientRequest(request_status=False).SerializeToString()
        
        elif request.WhichOneof('Type') == 'publishArticle':
            article = server_pb2.Article()
            article = request.publishArticle
            status = self.PublishArticle(article).SerializeToString()
            return status

        elif request.WhichOneof('Type') == 'getArticle':
            reqArticle = server_pb2.RequestMessage()
            reqArticle = request.getArticle
            matchedArticleList = self.GetArticles(reqArticle).SerializeToString()
            return matchedArticleList
            
    def JoinServer(self, request):
        print(f"JOIN REQUEST FROM {request.client_uuid}")
        if(len(self.clientelle) >= MAXCLIENTS or request.client_uuid in self.clientelle):
            return server_pb2.StatusOfClientRequest(request_status=False)
        self.clientelle.append(request.client_uuid)
        return server_pb2.StatusOfClientRequest(request_status=True)

    def LeaveServer(self, request):
        print(f"LEAVE REQUEST FROM {request.client_uuid}")
        prevlen = len(self.clientelle)
        self.clientelle[:] = (client for client in self.clientelle if (client != request.client_uuid))
        newlen = len(self.clientelle)
        return server_pb2.StatusOfClientRequest(request_status = (prevlen > newlen))

    def GetArticles(self, request):
        print(f"GET ARTICLE REQUEST FROM {request.client_uuid}")
        if((request.client_uuid not in self.clientelle) or not (is_valid_date(f"{request.day} {request.month} {request.year}"))):
            return server_pb2.ArticleList(status=False)
        matchedArticleList = server_pb2.ArticleList(status=True)
        for article in self.articles:
            if(articleMatches(request, article)):
                matchedArticleList.articles.append(article)

        return matchedArticleList

    def PublishArticle(self, request):
        print(f"ARTICLE PUBLISH FROM {request.client_uuid}")
        request.year = date.today().year
        request.month = date.today().month
        request.day = date.today().day
        content = request.content 
        author = request.author 

        emptyTopic = (request.SPORTS==False and request.FASHION==False and request.POLITICS==False)
        if((request.client_uuid not in self.clientelle) or content.strip() == "" or author.strip() == "" or emptyTopic or len(content) > 200):
            return server_pb2.StatusOfClientRequest(request_status=False)

        self.articles.append(request)
        return server_pb2.StatusOfClientRequest(request_status=True)


def serve(server, socket):

    socket.bind("tcp://*:" + str(server.port))

    while True :

        print('\n' + str(server.name) + ' listening for incoming requests...\n')
        
        #  Wait for next request from client
        request = socket.recv()
        
        # Check which type of request and handles it accordingly, returns protobuf after Serializing to string
        reply = server.HandleRequest(request)

        # Send the reply 
        socket.send(reply)
 
if __name__ == '__main__':
	
    name = input("Enter server name: ")
    port = input("Enter port: ")

    s = Server(name, 'localhost', port)

    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    if(s.RegisterAsServer(socket)):
        socket = context.socket(zmq.REP)
        serve(s, socket)
		
