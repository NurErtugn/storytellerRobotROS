import asyncio
import websockets
import threading
from threading import Thread
import time
import functools
from http.server import BaseHTTPRequestHandler, HTTPServer

lock = threading.Lock() #ensures that only one threadcan access the shared resources in a multithread env.  
global_data = None #this is a global variable (because it is defined outside of any function ) accessible from any part of the code . holds data  received by the client 
global_data_received = False #flag to indicate whether data has been received from the client 
t = None #initialize a variable to fold the thread object, ref to a thread obj of the execution

clients= set()
#Handler for the server
async def handler(websocket, path, callback):
    clients.add(websocket) #register new client
    try:
       
       async for message in websocket:
            print(f"Received message from {websocket.remote_address}: {message}")
            #check message type
            if isinstance(message,str):
                print(f"[server.py]: Received user input from the web browser : {str(message)}")
                data = str(message) 
                if(data == "close"): #if the client sends "close", close the connection and exit the program
                    callback(data) #new line #execute callback function w the received data 
                    await websocket.close() #close the websocket connection
                    exit(0) #exit the program 
                callback(data) #execute the callback function w received data
                
    finally: 
        clients.remove(websocket)

#Run the server       
def run_server(callback):
    loop = asyncio.new_event_loop() 
    asyncio.set_event_loop(loop) #set loop as the current event loop for the current OS thread
    loop1 = asyncio.get_event_loop() #get the current event loop 
    start_thread = websockets.serve(functools.partial(handler, callback=callback), "localhost", 10000) 
    loop1.run_until_complete(start_thread)  
    loop1.run_forever() 

async def send_data(feedback):
    if clients:
        print(f"[server.py>send_data]: Received user input from state machine")
        await asyncio.wait([client.send(feedback) for client in clients])
    else :
        print("no connected clients")

def main_callback(data): 
    global lock #global variable 
    global global_data
    global global_data_received #flag to tell yes i received the data , access to the lock variable outside

    print("before lock")
    lock.acquire() 

    print("after lock")
    
    global_data_received = True
    global_data = data
    lock.release() #release the locks

#Wait for a response from the client (web module)
def await_response():
    global lock
    global global_data
    global global_data_received
    while True: #function enters to an infinite loop  continuously to check the received data 
        lock.acquire() #allows only one thread to access to shared data 
        if(global_data_received): #new data is avaliable to be processed 
            global_data_received = False #reset 
            temp = global_data
            lock.release()
            return temp #return the received data 
        lock.release()
        time.sleep(0.1)

#Start a new thread for the server
def start_thread():
    global t
    t = Thread(target=run_server, args=(main_callback,)) # target = function to be executed by the thread, args = arguments to be passed to the target function
    t.start()
   
def join_thread():
    global t
    t.join()

if __name__ == "__main__":    
    print("thread started")
    start_thread()


