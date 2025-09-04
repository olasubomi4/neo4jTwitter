import json
from collections import deque

import pandas as pd

class ResponseObject:
    def __init__(self):
        self.__responseMessage=""
        self.__responseStatus=False
        self.__body=None


    def setResponseMessage(self,message):
        self.__responseMessage=message

    def setResponseStatus(self,status):
        self.__responseStatus=status

    def getResponseMessage(self):
        return self.__responseMessage

    def getResponseStatus(self):
        return self.__responseStatus

    def getBody(self):
        return self.__body

    def setBody(self,body):
        self.__body=body


    def jsonfyResponse(self):
        if self.__body is None:
            self.__body="{}"
        response = {
            "responseMessage": self.getResponseMessage(),
            "responseStatus": self.getResponseStatus(),
            "responseBody": json.loads(self.getBody())
        }
        return response