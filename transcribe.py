import time


import lib
import lib.server as server
import lib.workerBase as workerBase

class worker(lib.workerBase.workerBase):    
    
    def worker(self, entry, metadata):
        with open("/tmp/transcribe.log", "a") as log:
            log.write ("%d %s %s\n" % (metadata['time'], metadata['socket_name'], entry))
    
 
        
if __name__=="__main__":
    s = server.server()
    w = worker().run()
    s.mkInstance('tcp/ip', ('0.0.0.0', 4000), w)
    s.mkInstance('fifo', '/tmp/fifo', w)
    while 1:
        time.sleep(10)
        True
