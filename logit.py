#!/usr/bin/pythonal
"""
Simple module to send log messages to remote host
"""
from __future__ import print_function
import os
import time
import sys
import logging
import requests
import types
import jsonpickle
import uuid
import json
import shutil
from datetime import datetime
import calendar
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from logging import DEBUG, WARNING, ERROR
from sys import getsizeof, stderr
from itertools import chain
from collections import deque
try:
    from reprlib import repr
except ImportError:
    pass



def getUnixTimeStamp():
    """
    Returns current unix time stamp
    """
    return calendar.timegm(datetime.utcnow().utctimetuple())

## {{{ http://code.activestate.com/recipes/577504/ (r3)
## http://opensource.org/licenses/mit-license.php
def total_size(o, handlers={}, verbose=False):
    """ Returns the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: dict_handler,
                    set: iter,
                    frozenset: iter,
                   }
    all_handlers.update(handlers)     # user handlers take precedence
    seen = set()                      # track which object id's have already been seen
    default_size = getsizeof(0)       # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:       # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        if verbose:
            print(s, type(o), repr(o), file=stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)



#######################


#generate headers. add authentication headers here.
headers = {'content-type': 'application/json'}
#endpoint: EDIT THIS!
endpoint = 'http://localhost:8085/client'
#KB
maxSize=20
cachedFilesPath='logit/'
cachedArchivePath= 'logit-archive/'
cachedFileExtensionSuffix='.log'
#if cacheEnabled all logs are cached before uploading
cacheEnabled=True
cacheArhive=True
#maxAge
#cache



class Singleton(type):
    """
    A Metaclass. Logging is one of the use cases where such implementation is actually useful.
    http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]




class Node(object):
    """
    Parent payload document
    """
    def __init__(self, name):
        self._name = name
        self._children = {}
        self._parent = None
       

    def add_child(self, key, child):
       self._children[key]=child
        

    def remove_child(self,key):
        self._children.pop(key)

    





class AppPayload(Node):
    """
    Dict of payloads at app level
    maxSize:maximum file size
    maxAge: maximum age to keep it around
    cache:boolean, if enabled saves to cache before uploading. Always saves to cache if fails to 
    connect to remote host.
    """
    def __init__(self,project_tag, app_tag):
        Node.__init__(self,app_tag)
        self.app_tag=app_tag
        self.project_tag=project_tag
        

    def __str__(self):
        ret_str ='AppPayload "%s"\n' %self._name
        for k, v in self._children.items():
            ret_str += k+ ' : ' + repr(v)
        return ret_str

    def __repr__(self):
        return self.__str__()


class Payload(Node):
    """
    Log Payload at method/class/module level
    uuid: uuid1 signature per log
    Store individual log messages for writing to local file or uploading to server
    """
    def __init__(self,tag,uuid):
        Node.__init__(self, tag)
        self.uuid = uuid
        self.tag=tag

    def __str__(self):
        ret_str ='Payload "%s"\n' %self._name
        for k, v in self._children.items():
            ret_str += k+ ' : ' + repr(v)
        return ret_str

    def __repr__(self):
        return self.__str__()



class Logit(Node,FileSystemEventHandler):
    """
    Logging wrapper
    is a project instance
    project_tag:project level tag
    app_tag:app level tag
    """
    __metaclass__ = Singleton

    def __init__(self, project_tag,app_tag):
        Node.__init__(self, project_tag)
        self.project_tag = project_tag
        self.app_tag=app_tag

        print(project_tag,app_tag)
       
        #create log and archive directories
        if not os.path.exists(cachedFilesPath):
            os.makedirs(cachedFilesPath)
        if not os.path.exists(cachedArchivePath):
            os.makedirs(cachedArchivePath)

        #setup directory change event handler
        event_handler = self
        self.observer = Observer()
        self.observer.schedule(event_handler, '.', recursive=True)
        self.start()
        
    def on_any_event(self, event):
        "If any file or folder is changed"
        #print ("changed !")
        self.updateCache()

    def updateCache(self):
        """
        Looks for .log files. uploads them. on upload success, deletes them.
        """
        for root, dirs, files in os.walk(cachedFilesPath):
             for file in files:
                if file.endswith(cachedFileExtensionSuffix):
                    path = os.getcwd()+'/'+cachedFilesPath+file
                    with open(path, mode='r') as f:
                        payload_json = f.read()
                        payload_obj=jsonpickle.decode(payload_json)
                        r= self.upload(payload_obj)
                        if isinstance(r, types.NoneType):
                            #do nothing
                            print("")
                        else:
                            if r.status_code == 200 :
                            #uploaded!
                                if cacheArhive:
                                    #move it to archive
                                    dst=os.getcwd()+'/'+cachedArchivePath+file
                                    shutil.move(path, dst)
                                    print("archived log: ", file)
                                else:
                                    #delete it
                                    os.remove(path)

    def upload(self,projectPayload):
        """
        Uploads app payload to remote host
        """
        encodedPayload = jsonpickle.encode(projectPayload, unpicklable=False)

        print("uploading log...",self.project_tag)
        try:
            r=requests.post(endpoint, data=encodedPayload, headers=headers)

            if r.status_code != 200 :
            #couldn't save to remote so cache to file
                print ("error! " , r.status_code)
            return r

        except requests.ConnectionError as e:
            print ('ConnectionError error',e)


        
    def cachePayload(self,encodedPayload):
        """
        Cache app payload on remote host failure or on cacheEnabled
        """
        filename = cachedFilesPath + str(self.project_tag) + ('_%d'%getUnixTimeStamp()) + cachedFileExtensionSuffix
        #print(filename)

        with open(filename, mode='w') as f:
            f.write(encodedPayload)


    def __str__(self):
        ret_str ='Logit "%s"\n' %self._name
        for k, v in self._children.items():
            ret_str += k + ' : ' + repr(v)
        return ret_str

    def __repr__(self):
        return self.__str__()


    def start(self):
        """
        Logging to remote host is now started
        """
        self.observer.start()
        

    def join(self):
        """
        Join
        """
        self.observer.join()

    def stop(self):
        """
        Logging to remote host is now stopped
        """
        self.observer.stop()
    def values(self):
        """
        Print all children
        """
        global count
        for k,v in self._children.items():
            for ik,jv in v._children.items():
                count+=1
                print (count,ik,jv)

    def setProjectTag(self,project_tag):
        self.project_tag=project_tag

    def setAppTag(self,app_tag):
        self.app_tag=app_tag

   
    def log(self, logfunc, tag, message, exc_info):
        """
        Logs messages per project/app. core logic here.
        """
        
        #Calls the actual logger function

       
        logfunc(tag + ': ' + message, exc_info=exc_info)


       
        #create new payload with uuid signature
        
        id=uuid.uuid1().bytes.encode('base64').rstrip('=\n').replace('/', '_')

       
        #reverse: uid.UUID(bytes=(id + '==').replace('_', '/').decode('base64'))
      
        payload=Payload(tag,id)
        payload.level=logfunc.__name__
        payload.message=message

        #lookup and append to AppPayload by app_tag.create new AppPayload if 
        #does not exist
        if self.app_tag in self._children:
            #append to existing app payload
            #print ('append to existing app payload')    
            self._children[self.app_tag].add_child(id,payload)
            
        else:
            #create new AppPayload
            #print ('create new AppPayload')
            app_payload=AppPayload(self.project_tag,self.app_tag)
            app_payload.add_child(id,payload)
            self.add_child(self.app_tag,app_payload)



        #project root
        p_size = 0
        for k,v in self._children.items():
            #app root
            appPayloadSize = total_size(v._children,verbose=False)/1024
            p_size+=appPayloadSize

        if p_size > maxSize:
            if cacheEnabled:
                 encodedPayload = jsonpickle.encode(self._children, unpicklable=False)
                 self.cachePayload(encodedPayload)
                 self._children.clear()
            else:
                #upload it
                    r=self.upload(self._children)
                    if r.status_code == 200 :
                       self._children.clear()



        
    def debug(self, tag, message, exc_info=False):
        """
        Log a debug-level message. 
        """ 
       
        self.log(logging.debug,tag, message, exc_info)

    
    def warning(self, tag, message, exc_info=False):
        """
        Log a warning-level message. 
        """
       
        self.log(logging.warning,tag, message, exc_info)
   
    def error(self, tag, message, exc_info=False):
        """
        Log an error-level message. 
        """
       
        self.log(logging.error,tag, message, exc_info)

   

        



   
