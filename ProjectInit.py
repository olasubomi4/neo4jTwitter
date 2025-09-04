from dotenv import load_dotenv

import os

from LoggingProxy import LoggingProxy
from repository.TwitterGraphRepository import TwitterGraphDAO

logger =LoggingProxy()
load_dotenv()
class ProjectInit:

    def __init__(self,twitterGraphDAO:TwitterGraphDAO):
        self.twitterGraphDAO=twitterGraphDAO
    def str_to_bool(self ,s:str):
        if s.lower() == 'true' or s=='1' or s.lower()=="yes":
            return True
        return False

    def is_a_first_time_user(self,):
        return self.str_to_bool(os.getenv('IS_FIRST_TIME_USER',"false"))

    def data_preparation(self):
        if self.is_a_first_time_user():
            logger.logging.info("performing data preparation")
            self.twitterGraphDAO.createInteractsRelationship()
            graphName="weightGraph"
            relationships="{INTERACTS:{orientation:'UNDIRECTED',properties:'weight'}}"
            try:
                self.weightedGraph= self.twitterGraphDAO.createGraphProjection(graphName,["User"],relationships)
            except Exception as e:
                self.twitterGraphDAO.dropGraphProjection(graphName)
                logger.logging.error(f"Could not create weighted graph due to {e}")
            self.twitterGraphDAO.writeDegreeResult(graphName)
            self.twitterGraphDAO.writePageRankResult(graphName)
            self.twitterGraphDAO.writeCommunityResult(graphName)
            self.twitterGraphDAO.writeBetweennessResult(graphName)
        else:
            logger.logging.info("skipping data preparation")




