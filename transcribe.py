import time, socket, sys, os

import helpers
import helpers.listenerBase as listenerBase
import helpers.workerBase as workerBase

class worker(helpers.workerBase.workerBase):    
    
    def worker(self, entry, metadata):
        with open("/tmp/transcribe.log", "a") as log:
            log.write ("%d %s %s\n" % (metadata['time'], metadata['socket_name'], entry))
    
class listenerServer(helpers.listenerBase.listenerBase):
    
    def open(self, conn=('127.0.0.1',65535), sock_type='tcp/ip', worker=None, buf=4096, backlog=5, **kwargs):
        if sock_type == "tcp/ip":
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif sock_type == "tcp/unix":
            self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        elif sock_type == "udp/ip":
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif sock_type == "udp/unix":
            self.s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(conn)
        self.s.listen(backlog)
        while 1: #keep waiting for new connections
            client, addr = self.s.accept()
            self.threadHandle(client=client, addr=addr, name=addr[0]+"."+str(addr[1]), worker=worker)
    
    #handle    
    def handle(self, client, addr, worker, **kwargs):
        socketfile = client.makefile()
        try:
            socketName = socket.gethostbyaddr(addr[0])[0]
        except socket.herror, e:
            sys.stderr.write(str(e)+": "+addr[0]+"\n")
            socketName = addr[0]
        while 1: #keep reading until the end
            try:
                line = socketfile.readline().strip("\n")
                if line != "":
                    #logLine = "%d %s %s" % (time.time(), socketName, line)
                    #print logLine
                    #client.send('< '+logLine+"\n> ")
                    worker.queue_line(line, {'time':time.time(), 'socket_name':socketName})
                else:
                    time.sleep(.5)
            except socket.error, e: # A socket error
                print (str(e))
                self.closeHandle(client, addr)
                sys.exit()
            except IOError, e:
                print (str(e)+"1")
                self.closeHandle(client, addr)
                sys.exit()
    
    #close        
    def closeHandle(self, client, addr):
        client.close()
        return True
        
    def close(self):
        self.s.close()
        sys.exit()
        return True

class listenerFile(helpers.listenerBase.listenerBase):
    def open(self, path='/tmp/file', listen_type='file', worker=None, **kwargs):
        if listen_type == "fifo":
            if os.path.exists(path) == False:
                sys.stderr.write("fifo: "+path+" did not exist making it")
                os.mkfifo(path)
        elif listen_type == "file":
            if os.path.exists(path) == False:
                sys.stderr.write("file: "+path+" does not exist")
                return False #just going to exist maybe will add some special condtion later
        
        self.threadHandle(path=path, worker=worker)
    
    def handle(self, path, worker, **kwargs):
        self.hostname = socket.gethostname()
        with open(path) as tailFile:
            tailFile.seek(0, os.SEEK_END)
            while 1:
                line = tailFile.readline().strip("\n")
                logLine = "%d %s %s" % (time.time(), self.hostname, line)
                if line != "":
                    worker.queue_line(line, {'time':time.time(), 'socket_name':self.hostname})
                else:
                    time.sleep(1)
    def close(self):
        sys.exit()

if __name__=="__main__":
    w = worker(pool_size=3, queue_size=2000000).run()
    s = listenerServer().mkInstance(conn=('0.0.0.0', 4000), worker=w, listen_type='tcp/ip')
    f = listenerFile().mkInstance(path='/tmp/fifo', worker=w, listen_type='file')
    l = listenerFile().mkInstance(path='/var/log/syslog', worker=w, listen_type='file')
    
    while 1:
        time.sleep(10)
        True
