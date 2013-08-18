import time, types, os, sys, signal
import multiprocessing

"""
This class is simple enough to allow workers which take incomming log lines and do things with them.
I really dont know what people will want to do with there logs and how they will want to output them
but this is where they will be able to control the output system.
"""

workers = {}

def workerTarget(*args, **kw):
    global workers
    method_name = args[0]
    return getattr(workers[args[0]], 'worker_loop')(*args[1:])

class workerBase(object):
    
    def __init__(self, name="master", pool_size=0, queue_size=1024):
        self.queue_size, self.pool_size, self.name = queue_size, pool_size, name
        self.queue_active = True
        self.workers_stopped = False
        
        signal.signal(signal.SIGINT, self.signal_handler) #shut down hoandler
        signal.signal(signal.SIGTERM, self.signal_handler) #shut down hoandler
        
        if self.pool_size == 0: #if no size is set lets use the total number of processses the system have
            self.pool_size = multiprocessing.cpu_count()
        
        global workers
        workers[name] = self
    
    def run(self):    
        if isinstance (self.worker_loop, types.MethodType):
            args = list()
            args.insert(0, self.name)
        
        self.queue = multiprocessing.Queue(self.queue_size)
        self.pool = multiprocessing.Pool(self.pool_size)
        for x in range(0, self.pool_size): #avoid needing to run map but still get all the workers to start up
            self.pool.apply_async(workerTarget, args)
        return self
        
    def queue_line(self, entry, metadata): #put the data in the queue
        if self.queue_active == True:
            try:
                self.queue.put([entry, metadata], False) #should come up with a better method that the server will wait on false and try to queue there
            except Queue.Full, e:
                print (str(e))
            except Exception, e:
                sys.stderr.write("queue_line: "+str(e)+"\n")
        else:
            return False
    
    def worker_stop(self):
        self.queue_active = False
        self.stop_loop = True
        
        if self.workers_stopped == False:
            while self.stop_loop == True:
                if self.queue.empty == False:
                    time.sleep(1)
                    sys.stderr.write("Waiting for queue: "+queue+" to reach 0, currntly at "+str(self.queue.qsize()))
                else:
                    try:
                        self.queue.close() # close the queue now since its empty
                    except:
                        pass
                    sys.stderr.write("Giving the workers a little more time to finish there last task\n")
                    self.stop_loop = False
                    self.workers_stopped = False
                    time.sleep(2)
                    try:
                        sys.stderr.write("Closing pool\n")
                        self.pool.close()
                        sys.stderr.write("after pool close\n")
                    finally:
                        sys.stderr.write("")
                        exit()
        sys.stderr.write("")
        exit(False)
            
    def worker_loop(self): #to simplyfiy things this is the loop that feeds the data into the worker so users just need to handle data entry or what ever
        while self.queue.empty == False or self.workers_stopped == False:
            try:
                #sys.stderr.write("Queue size: "+str(self.queue.qsize())+" @ "+str(time.time())+"\n")
                todo = self.queue.get()
                #print sys.stderr.write("Queue object: "+str(todo)+"\n")
                self.worker(todo[0], todo[1])
                #time.sleep(1)
            except Queue.Empty, e:
                print (str(e))
                time.sleep(1)
            except Exception, e:
                sys.stderr.write("worker_loop: "+str(e)+"\n")
                
        exit()
        return True
        
    def worker(self, entry, metadata):
        raise NotImplementedError( "Write a method that gets run as a callback once for every log entry worker(self, entry, metadata)" )

    def signal_handler(self, signal, frame):
        self.worker_stop()
