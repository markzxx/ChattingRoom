import json
import _thread
from tkinter import *
import time
from mysocket import *
import random
#normal socket setting
server_addr = "10.20.13.19"
server_port = 6666
ClientSocket = socket(AF_INET,SOCK_DGRAM)

#when a client is open, send connect to server
def connect():
    message = {}
    message["type"] = "connect"
    message["name"] = text_name.get()
    ClientSocket.sendto(json.dumps(message).encode(), (server_addr, server_port))

#when a client is close, send disconnect to server
def disconnect():
    message = {}
    message["type"] = "disconnect"
    ClientSocket.sendto(json.dumps(message).encode(), (server_addr, server_port))
    ClientSocket.close()
    root.quit()

#when recieve a userlist update message, update the userlist
def update_userlist(message):
    text_userlist.delete('0.0',END)
    message.pop("type")
    for user in message.values():
        text_userlist.insert(END,user+"\n")

#when recieve a chat message, prin it on the main board
def print_in_main(message):
    text_msglist.insert(END, message["name"]+" "+message["time"]+"\n", 'green')
    text_msglist.insert(END, message["content"]+"\n", 'green')

#get message from server, action according the message type
def get_message():
    while 1:
        message, server_address = ClientSocket.recvfrom(2048)
        message = json.loads(message.decode())
        print(message)
        if message["type"] == "chat":
            print_in_main(message)
        elif message["type"] == "userlist":
            update_userlist(message)
        elif message["type"] == "connect":
            text_msglist.insert(END, message['content'] + '\n', 'blue')

#send chating message to server, recording your name and time
def send_message():
    message = {}
    message["type"] = "chat"
    message["name"] = text_name.get()
    message["time"] = time.strftime(" %Y-%m-%d %H:%M:%S",time.localtime())
    message["content"] = text_input.get('0.0', END)
    text_input.delete('0.0', END)
    print(message)
    ClientSocket.sendto(json.dumps(message).encode(), (server_addr, server_port))

#a small function for user's name
def random_name():
    i = random.randrange(len(first_name))
    j = random.randrange(len(last_name))
    return first_name[i]+last_name[j]

#here are gui part, easy but complex
root = Tk()
root.title('Chatting room')
root.protocol("WM_DELETE_WINDOW",disconnect) #add a listener for close action

first_name = ["愤怒的","英勇的","残暴的","逆天的"]
last_name = ["学霸","预言家","小鸟","德玛西亚"]

frame_left_main   = Frame(width=380, height=300, bg='white')
frame_left_input  = Frame(width=280, height=70, bg='white')
frame_left_name  = Frame(width=100, height=25)
frame_left_button  = Frame(width=100, height=25)
frame_right     = Frame(width=170, height=400, bg='white')

text_msglist = Text(frame_left_main,width = 380)
text_userlist = Text(frame_right)
text_input = Text(frame_left_input,width = 280)
text_name = Entry(frame_left_name)
text_name.insert(END,random_name())
button_sendmsg = Button(frame_left_button, text='发送', command=send_message)

text_msglist.tag_config('green', foreground='#008B00')
text_msglist.tag_config('blue', foreground='#00008b')

frame_left_main.grid(row=0, column=0,columnspan=2)
frame_left_input.grid(row=1, column=0,rowspan=2)
frame_left_name.grid(row=1, column=1)
frame_left_button.grid(row=2, column=1)
frame_right.grid(row=0, column=2, rowspan=3,padx = 5,pady = 5)
frame_left_main.grid_propagate(0)
frame_left_input.grid_propagate(0)
frame_left_name.grid_propagate(0)
frame_left_button.grid_propagate(0)
frame_right.grid_propagate(0)

text_msglist.grid()
text_input.grid()
text_name.grid()
button_sendmsg.grid()
text_userlist.grid()

if __name__ =='__main__':
    connect()
    #start a new thread to get message
    _thread.start_new_thread(get_message,())
    root.mainloop()
