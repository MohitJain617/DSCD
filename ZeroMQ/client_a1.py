import zmq
import registryserver_pb2
import server_pb2

import uuid

REGISTRY_SERVER_ADDR = 'localhost:5555'
TIMEOUT = 10000   # 10sec

class Client:
    
    def __init__(self) -> None:
        self.id = str(uuid.uuid1())

    def GetServerList(self, context):

        print("Connecting to Registry server…")
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://"+REGISTRY_SERVER_ADDR)

        request = registryserver_pb2.RegistryServerMessage(clientDetails = registryserver_pb2.ClientDetails(client_uuid=self.id)).SerializeToString()
        socket.send(request)

        message = socket.recv()
        response = registryserver_pb2.ServerList()
        response.ParseFromString(message)

        print('Server List Recieved from Registry Server')
        print('-'*30)
        for ss in response.server_list:
            print(f"{ss.name} - {ss.addr}")
        
        socket.close()

    def JoinServer(self, context):
        
        addr = input("Address of server (ip:port) = ")
        try:
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://"+addr)
            request = server_pb2.ServerMessage(clientDetails = server_pb2.ClientDetails(client_uuid=self.id, join = True)).SerializeToString()

            socket.setsockopt(zmq.RCVTIMEO, TIMEOUT)
            socket.send(request)
            message = socket.recv()
            response = server_pb2.StatusOfClientRequest()
            response.ParseFromString(message)
            socket.close()

            if(response.request_status == True):
                print("SUCCESS")
            elif(response.request_status == False):
                print("FAIL")
        
        except zmq.error.Again:
            print("Receive timeout occurred - no response received within",  (TIMEOUT//1000), "seconds")

        except Exception as e:
            print('Invalid Server Address')

        finally:
            socket.close()
            return 

    def LeaveServer(self, context):
        addr = input("Address of server (ip:port) = ")
        
        try:
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://"+addr)
            request = server_pb2.ServerMessage(clientDetails = server_pb2.ClientDetails(client_uuid=self.id, leave = True)).SerializeToString()
            socket.setsockopt(zmq.RCVTIMEO, TIMEOUT)
            socket.send(request)
            message = socket.recv()
            response = server_pb2.StatusOfClientRequest()
            response.ParseFromString(message)
            socket.close()

            if(response.request_status == True):
                print("SUCCESS")
            else:
                print("FAIL")

        except zmq.error.Again:
            print("Receive timeout occurred - no response received within",  (TIMEOUT//1000), "seconds")

        except Exception as e:
            print('Invalid Server Address')

        finally:
            socket.close()

    def GetArticles(self, context):
        
        addr = input("Address of server (ip:port) = ")
        tag = input("Article tag (sports, fashion, politics, else all): ").lower()
        author = input("Author name (or blank):") 
        day = int(input("day: "))
        month = int(input("month: "))
        year = int(input("year: "))

        socket = context.socket(zmq.REQ)

        try : 

            reqArticle = server_pb2.RequestMessage(client_uuid=self.id)
            
            if(tag == 'sports'):
                reqArticle.SPORTS = True
            elif(tag == 'fashion'):
                reqArticle.FASHION = True 
            elif(tag == 'politics'):
                reqArticle.POLITICS = True 
            else:
                reqArticle.allTags = True
            
            reqArticle.author = author
            reqArticle.day = day
            reqArticle.month = month
            reqArticle.year = year

            reqArticleMsg = server_pb2.ServerMessage(getArticle = reqArticle)

            socket.connect("tcp://"+addr)
            request = reqArticleMsg.SerializeToString()

            socket.setsockopt(zmq.RCVTIMEO, TIMEOUT)
            socket.send(request)

            message = socket.recv()
            response = server_pb2.ArticleList()
            response.ParseFromString(message)
            socket.close()

            if(response.status == False):
                print("FAIL")
            else:
                print('Articles Recieved from Server')
                print('-'*40)
                cnt = 1
                for article in response.articles:
                    print(cnt)
                    artTag = "SPORTS" if (article.SPORTS) else "FASHION" if (article.FASHION) else "POLITICS"
                    print(artTag)
                    print(article.author)
                    print(f"{article.day}/{article.month}/{article.year}")
                    print(article.content)
                    cnt+=1

        except zmq.error.Again:
            print("Receive timeout occurred - no response received within", (TIMEOUT//1000), "seconds")

        except Exception as e:
            print(e)
            print('Invalid Server Address')
        
        finally:
            socket.close()
            return
 
    def PublishArticle(self, context):
        
        addr = input("Address of server (ip:port) = ")
        tag = input("Article tag (sports, fashion, politics): ").lower() 
        author = input("Enter author name: ")
        content = input("Enter content: ")

        socket = context.socket(zmq.REQ)

        try : 
            pubArticle = server_pb2.Article(author=author,content=content,client_uuid=self.id)
            if(tag == 'sports'):
                pubArticle.SPORTS = True
            elif(tag == 'fashion'):
                pubArticle.FASHION = True 
            elif(tag == 'politics'):
                pubArticle.POLITICS = True 
            else:
                raise ValueError("Invalid Tag")
            
            pubArticleMsg = server_pb2.ServerMessage(publishArticle = pubArticle)

            request = pubArticleMsg.SerializeToString()

            socket.connect("tcp://"+addr)
            socket.setsockopt(zmq.RCVTIMEO, TIMEOUT)
            socket.send(request)

            message = socket.recv()
            response = server_pb2.StatusOfClientRequest()
            response.ParseFromString(message)
            socket.close()

            if(response.request_status == True):
                print("SUCCESS")
            else:
                print("FAIL")
        
        except zmq.error.Again:
            print("Receive timeout occurred - no response received within",  (TIMEOUT//1000), "seconds")

        except Exception as e:
            print('Invalid Server Address')
        
        finally:
            socket.close()
            return
		
if __name__== '__main__':

    context = zmq.Context()

    client = Client()
    ch = 'x'

    while(ch != 'q'):

        print("---------------####----------------")
        print("Get server list (g) | Join Server (j) | Leave Server (l) | Get Article (a) | Publish (p) | Quit (q):")
        
        ch = input().lower()
        if(ch == 'q'):
            break 
        elif(ch == 'g'):
            client.GetServerList(context)
        elif(ch == 'j'):
            client.JoinServer(context)
        elif(ch == 'l'):
            client.LeaveServer(context)
        elif(ch == 'a'):
            client.GetArticles(context)
        elif(ch == 'p'):
            client.PublishArticle(context)
        else:
            print("Invalid input")
