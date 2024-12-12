import os
from py2neo import Graph
import pandas as pd

from dotenv import load_dotenv

class Neo4J:
    def __init__(self):
        load_dotenv();
        self.__dbUser = os.getenv('NEO4J_USER')
        self.__dbPass = os.getenv('NEO4J_PASS')
        self.__dbHost = os.getenv('NEO4J_HOST')
        self.connection = None

    def getConnection(self):
        try:
            if self.connection == None:
               self.connection=Graph(self.__dbHost, auth=(self.__dbUser,self.__dbPass))
            return self.connection
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Neo4j: {e}")
