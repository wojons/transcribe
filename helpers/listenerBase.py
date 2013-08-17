import random, time, os, sys, threading, signal

class listenerBase():

    def __init__(self):
        self.threads = {'listener' : {}, 'listeners' : {}}
        signal.signal(signal.SIGINT, self.signal_handler) #shut down hoandler
        signal.signal(signal.SIGTERM, self.signal_handler) #shut down hoandler
    
    #open    
    def mkInstance(self, **kwargs):
        if kwargs.has_key('name') == False:
            kwargs['name'] = self.randomName()
        
        self.threads['listener'][kwargs['name']] = threading.Thread(target=self.open, kwargs=kwargs)
        
        #daemonize and then start the thread
        self.threads['listener'][kwargs['name']].daemon=True
        self.threads['listener'][kwargs['name']].start()
    
    def threadHandle(self, **kwargs):
        if kwargs.has_key('name') == False:
            kwargs['name'] = self.randomName()
        
        self.threads['listeners'][kwargs['name']] = threading.Thread(target=self.handle, kwargs=kwargs)
        self.threads['listeners'][kwargs['name']].daemon=True
        self.threads['listeners'][kwargs['name']].start()
    
    def randomName(self):
        return str(time.time)+str(random.random)
    
    def open(self, *args, **kwargs):
        raise NotImplementedError( "Write a method" )
    def handle(self):
        raise NotImplementedError( "Write a method" )
    def close(self):
        raise NotImplementedError( "Write a method" )
    
    def signal_handler(self, signal, frame):
        self.close()
    #def closeFile(self delete=False):
