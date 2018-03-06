import json
from mysocket import *
#get host ip by a function
def get_host_ip():
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(('114.114.114.114', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

#normal setting
ip_addr = get_host_ip()
port = 6666
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((ip_addr,port))
user_dict = {}
print("ip:{},port:{},Ready to serve.".format(ip_addr,port))

#this function to broadcast something to every user in user dictionary
def broadcasting(raw_broadcast):
    broadcast = json.dumps(raw_broadcast).encode()  #all data transfer in json format
    for address in user_dict.keys():
        serverSocket.sendto(broadcast, address)

#update userlist, when a new user connect , a user disconnect or somebody rename
def update_userlist():
    broadcast = {}
    broadcast["type"] = "userlist"
    for key,value in user_dict.items():
        broadcast[str(key)] = value
    broadcasting(broadcast)

#when a new user connect, record and update
def user_cennect():
    global user_dict
    user_dict[clientAddress] = message["name"]
    update_userlist()

#when a user disconnect, remove and update
def user_disconnect():
    global user_dict
    if clientAddress in user_dict.keys():
        user_dict.pop(clientAddress)
    update_userlist()

#when somebody rename, change the list and update
def rename():
    global user_dict
    user_dict[clientAddress] = message['name']
    update_userlist()

#finally somebody send a chatting message, forward it to everybody in list
def chatting():
    if clientAddress not in user_dict.keys():
        user_cennect()
    broadcast = {}
    broadcast["type"] = "chat"
    broadcast["name"] = message["name"]
    broadcast["time"] = message["time"]
    broadcast["content"] = message["content"]
    broadcasting(broadcast)
    
while 1:
    raw_message = ""
    clientAddress = ""
    #here is a loop to guarantee a correct message, if not do that, when a client shut down his program suddenly will have a ConnectionResetError
    while not (clientAddress and raw_message):
        try:
            raw_message, clientAddress = serverSocket.recvfrom(2048)
        except:
            pass
    message = json.loads(raw_message.decode())
    print(message)
    message_type = message['type']
    response = {}
    #action depends on the type of message
    if message_type == "connect":
        response["type"] = "connect"
        response["content"] = message['name'] + ",welcome to chatting room!"
        user_cennect()
    elif message_type == "disconnect":
        user_disconnect()
    elif message_type == "chat":
        if message['name']!= user_dict[clientAddress]:
            rename()
        chatting()
        response["type"] = "chat_respone"
        response["status"] = "OK"
    else:
        response["type"] = 'error'
    serverSocket.sendto(json.dumps(response).encode(), clientAddress)
 