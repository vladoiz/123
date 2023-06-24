#! python3
# Defining a server for sending and receiving messages
# through network, applying 2 child-thread
import socket, sys, threading,time


PORT = 1337
HOST = '46.19.64.214'#socket.gethostname()



#SHOULD BE 2 or 5
MAXUSER = int(input("User limit (2 or 5): "))

STARTLEVEL = 1

class ThreadClient(threading.Thread):
    """heritance of a thread-object to communicate with the client"""
    def __init__(self, conn, thname):
        threading.Thread.__init__(self, name=thname)
        self.conn = conn
    
    def run(self):
        global glob_ready, STARTLEVEL
        #Communication with client
        name= self.getName()        # All threads have an ID
        while True:
            try:
                start=self.conn.recv(1).decode('UTF-8')
                if start!=chr(0):
                    print("start:",start)
                else:
                    msgClient=''
                    while True:
                        curr=self.conn.recv(1).decode('UTF-8')
                        if curr==chr(0):break
                        msgClient+=curr
                print(msgClient)
            except ConnectionResetError:
                del conn_Cli[name]
                return
            except Exception as e:
                print(e)
                print(msgClient)
            if msgClient=='#fin#' or msgClient=="":
                break
            if msgClient=='help.get':
                x=True
                locking.acquire()
                for client in conn_Cli:
                    if client!=name:
                        sendmsg(conn_Cli[name],bytes("SERVER>>> "+client+' online.', 'utf-8'))
                        x=False
                        #time.sleep(0.5)
                if x: sendmsg(conn_Cli[name],bytes("SERVER>>> Currently you are the only one online", 'utf-8'))
                sendmsg(conn_Cli[name],bytes("#LEVEL#%s"%STARTLEVEL, 'utf-8'))
                locking.release()
                continue
            if msgClient.startswith("!level"):
                try:
                    STARTLEVEL=int(msgClient.split()[1])
                except:
                    sendmsg(conn_Cli[name], bytes("Server>>> Invalid syntax!", 'utf-8'))
                    continue
                for client in conn_Cli:
                    if client!=name:
                        message="%s> %s" % (name, msgClient)
                        sendmsg(conn_Cli[client],bytes(message, 'utf-8'))
                    sendmsg(conn_Cli[client],bytes("#LEVEL#%s"%STARTLEVEL, 'utf-8'))
                continue
            if msgClient.startswith("#pic#"):
                glob_ready=False
                message= msgClient+"#pic#"+name
                print(message)
                locking.acquire()
                for client in conn_Cli:
                    if client!=name:
                        sendmsg(conn_Cli[client],bytes(message, 'utf-8'))
                img=b''
                a=0
                length=int(msgClient.split("#pic#")[1])
                #sendmsg(conn_Cli[name],bytes("#prog#"+str(len(str(length))), 'utf-8'))
                time.sleep(0.15)
                while a<length: 
                    msgImg=self.conn.recv(4096)
                    img+=msgImg
                    a+=len(msgImg)
                    for client in conn_Cli:
                        if client!=name:
                            conn_Cli[client].send(msgImg)
                    #sendmsg(conn_Cli[name],bytes("#prog#"+str(a),'utf-8'))
                locking.release()
                glob_ready=True
                continue
            if msgClient.startswith("#GAME#"):
                locking.acquire()
                for client in conn_Cli:
                    if client!=name:
                        sendmsg(conn_Cli[client],bytes(msgClient,'utf-8'))
                locking.release()
                continue
            message="%s> %s" % (name, msgClient)
            print(message)
            locking.acquire()
            for client in conn_Cli:
                if client!=name:
                    sendmsg(conn_Cli[client],bytes(message, 'utf-8'))
            locking.release()


        # Closing the connection 
        self.conn.close()           # Server side connection close
        locking.acquire()
        for client in conn_Cli:
            if client!=name:
                sendmsg(conn_Cli[client],bytes("#DELETE#%s"%name, 'utf-8'))
                sendmsg(conn_Cli[client],bytes("SERVER>>> %s Has disconnected."%name, 'utf-8'))
        locking.release()
        del conn_Cli[name]          # deleting reg from dictionary
        print("Client, %s has disconnected."%name)
        #End of thread


def sendmsg(conn,msg):
    conn.send(bytes(chr(0), 'utf-8'))
    conn.send(msg)
    conn.send(bytes(chr(0), 'utf-8'))

# Initializing server - creating socket
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    mySocket.bind((HOST, PORT))
except socket.error:
    print("Didn't manage to bind the socket with this address..")
    time.sleep(2)
    sys.exit()
print("Server is ready, waiting...")
mySocket.listen()

# Managing connecting clients
conn_Cli={}
locking=threading.Lock()
glob_ready=True
while True:
    try:
        connec, addr = mySocket.accept()
        # Received a connection, initializing new thread
        name=connec.recv(1024).decode('UTF-8')
        if name in conn_Cli:
            name=name+'({0})'.format(addr[1])
        while len(conn_Cli)==MAXUSER:
            connec.send(bytes('no', 'utf-8'))
            continue
        th= ThreadClient(connec,name)
        while not glob_ready:
            continue
        th.start()
        # Registering the connection
        it= th.getName()
        conn_Cli[it]=connec
        print("Client, %s has connected, IP address %s, port %s." \
                                % (it, addr[0], addr[1]))
        locking.acquire()
        connec.send(bytes(name, 'utf-8'))
        sendmsg(connec,bytes("SERVER>>> Successful connection, welcome, %s"%it, 'utf-8'))
        sendmsg(connec,bytes("#MAXUSER#%s"%MAXUSER, 'utf-8'))
        for client in conn_Cli:
            if client!=name:
                sendmsg(conn_Cli[client], bytes("SERVER>>> Client %s connected to the server, IP address %s, port %s." \
                                % (it, addr[0], addr[1]), 'utf-8'))
                sendmsg(conn_Cli[client],bytes("#PLAYER#%s"%name, 'utf-8'))
                sendmsg(connec,bytes("#PLAYER#%s"%client, 'utf-8'))
        locking.release()
    except Exception as e:
        print(e)
