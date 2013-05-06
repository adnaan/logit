#!/usr/bin/python
"""
Simple module to save log messages to remote server
"""
import os.path
import logging
import traceback
import requests
import collections
import jsonpickle
import uuid


from logging import DEBUG, WARNING, ERROR

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

    show_path = True

   
    def log(self, logfn, message, exc_info):
        cname = ''
        location = ''
        fn = ''
        tb = traceback.extract_stack()
        if len(tb) > 2:
            if self.show_path:
                loc = '(%s:%d):' % (os.path.basename(tb[-3][0]), tb[-3][1])
            fn = tb[-3][2]
            if fn != '<module>':
                if self.__class__.__name__ != Logit.__name__:
                    fn = self.__class__.__name__ + '.' + fn
                fn += '()'

        """
        Calls the actual logger function

        """
        logfn(location + cname + fn + ': ' + message, exc_info=exc_info)


        """
        create payload 
        """
        id=uuid.uuid1().bytes.encode('base64').rstrip('=\n').replace('/', '_')

        """"
        reverse: uid.UUID(bytes=(id + '==').replace('_', '/').decode('base64'))
        """
        payload=Payload(id)
        payload.tag=self.tag
        payload.level=logfn.__name__
        payload.message=message

        """
        generate headers

        """
        headers = {'content-type': 'application/json'}


        """
        endpoint
        """

        endpoint = 'http://localhost:8085/client'

        """
        save it
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

        



   
