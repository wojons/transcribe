import socket
import time
import threading
import os, sys

class server():

    def __init__(self):
        self.threads = {'server' : {}, 'client' : {}, 'file' : {}}
        self.hostname = socket.gethostname()
    
    #open    
    def mkInstance(self, sock_type, conn):
        if sock_type != "fifo" and sock_type != "file": #create a socket
            self.threads['server'][conn] = threading.Thread(target=self.openSocket, kwargs={'conn' : conn, sock_type:sock_type})
        else:
            print sock_type
            self.threads['server'][conn] = threading.Thread(target=self.openFile, kwargs={'conn' : conn, sock_type:sock_type})
        
        #daemonize and then start the thread
        self.threads['server'][conn].daemon=True
        self.threads['server'][conn].start()
    
    
    def openSocket(self, conn=('127.0.0.1',65535), sock_type='tcp/ip', buf=4096, backlog=5, **kwargs):
        if sock_type == "tcp/ip":
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif sock_type == "tcp/unix":
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        elif sock_type == "udp/ip":
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif sock_type == "udp/unix":
            s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        
        s.bind(conn)
        s.listen(backlog)
        while 1: #keep waiting for new connections
            client, address = s.accept()
            self.threads['client'][conn] = threading.Thread(target=self.handleSocket, kwargs={'client':client, 'addr':address})
            self.threads['client'][conn].daemon=True
            self.threads['client'][conn].start()
        
    def openFile(self, conn='/tmp/file', sock_type='file', **kwargs):
        if sock_type == "fifo":
            if os.path.exists(conn) == False:
                sys.stderr.write("fifo: "+conn+" did not exist making it")
                os.mkfifo(conn)
        elif sock_type == "file":
            if os.path.exists(conn) == False:
                sys.stderr.write("file: "+conn+" does not exist")
                return False #just going to exist maybe will add some special condtion later
        
        self.threads['file'][conn] = threading.Thread(target=self.handleFile, kwargs={'conn':conn})
        self.threads['file'][conn].daemon=True
        self.threads['file'][conn].start()
    
    #handle    
    def handleSocket(self, client, addr, **kwargs):
        socketfile = client.makefile()
        socketName = socket.gethostbyaddr(addr[0])[0]
        while 1: #keep reading until the end
            try:
                line = socketfile.readline().strip("\n")
                logLine = "%d %s %s" % (time.time(), socketName, line)
                print logLine
                client.send(logLine)
            except socket.error, e: # A socket error
                print (str(e))
                self.closeSocket(client, addr)
                sys.exit()
            except IOError, e:
                print (str(e)+"1")
                self.closeSocket(client, addr)
                sys.exit()
        
    def handleFile(self, conn):
        tailFile = open(conn)
        while 1:
            line = tailFile.readline().strip("\n")
            logLine = "%d %s %s" % (time.time(), self.hostname, line)
            if line != "":
                print line
    #close        
    def closeSocket(self, client, addr):
        client.close()
        return True
    
    #def closeFile(self delete=False):

if __name__=="__main__":
    s = server()
    s.mkInstance('tcp/ip', ('0.0.0.0', 4000))
    s.mkInstance('fifo', '/tmp/fifo')
    while 1:
        time.sleep(10)
        True
    
