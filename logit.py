#!/usr/bin/python
"""
Simple module to send log messages to remote host
"""
import os.path
import logging
import traceback
import requests
import collections
import jsonpickle
import uuid


from logging import DEBUG, WARNING, ERROR
"""
Log Payload
"""
class Payload(object):
    def __init__(self, uuid):
        self.uuid = uuid

    def __repr__(self):
        return 'Payload("%s")' % self.uuid


class Logit(object):
    """
    Logging wrapper
    """
    def __init__(self, tag):
        self.tag = tag

   
    def log(self, logfunc, message, exc_info):
        
        """
        Calls the actual logger function

        """
        logfunc(self.tag + ': ' + message, exc_info=exc_info)


        """
        create payload with uuid signature
        """
        id=uuid.uuid1().bytes.encode('base64').rstrip('=\n').replace('/', '_')

        """"
        reverse: uid.UUID(bytes=(id + '==').replace('_', '/').decode('base64'))
        """
        payload=Payload(id)
        payload.tag=self.tag
        payload.level=logfunc.__name__
        payload.message=message

        """
        generate headers. add authentication headers here.

        """
        headers = {'content-type': 'application/json'}


        """
        endpoint: EDIT THIS!
        """

        endpoint = 'http://localhost:8085/client'

        """
        post it
        """

        requests.post(endpoint, data=jsonpickle.encode(payload, unpicklable=False), headers=headers)



    def debug(self, message, exc_info=False):
        """
        Log a debug-level message. 
        """
        self.log(logging.debug, message, exc_info)

    def warning(self, message, exc_info=False):
        """
        Log a warning-level message. 
        """
        self.log(logging.warning, message, exc_info)

    def error(self, message, exc_info=False):
        """
        Log an error-level message. 
        """
        self.log(logging.error, message, exc_info)

    def __repr__(self):
        return 'Logit   ("%s")' % self.tag

        



   
