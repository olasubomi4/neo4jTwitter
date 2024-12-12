class ResponseObject:
    def __init__(self):
        self.__responseMessage=""
        self.__responseStatus=False
        self.__body={}

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