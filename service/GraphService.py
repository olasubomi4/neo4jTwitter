import json

from config.Neo4J import Neo4J
from dto.ResponseObject import ResponseObject
from repository.TwitterGraphRepository import TwitterGraphDAO


class GraphService:
    def __init__(self,TwitterGraphDAO):
        self.TwitterGraphDAO = TwitterGraphDAO
        self.relationships=['POSTS', 'REPLY_TO', 'RETWEETS', 'MENTIONS',"TAGS"]
        self.nodes=['User', 'Tweet','Hashtag']
        self.weightedRelationShip="{INTERACTS:{orientation:'UNDIRECTED',properties:'weight'}}"
        self.embeddingProperties="{embeddingDimension:64,randomSeed:7474,mutateProperty:'embedding'}"
    def recommendTweets(self,userName):
        responseObject=ResponseObject()
        graphName="recommendTweets";
        if self.TwitterGraphDAO.doesGraphProjectionExist(graphName):
            self.TwitterGraphDAO.dropGraphProjection(graphName)
        self.TwitterGraphDAO.createGraphProjection(graphName,self.nodes,self.relationships)
        self.TwitterGraphDAO.createGraphEmbeddingWithfastRP(graphName,self.embeddingProperties)
        recommendTweets= self.TwitterGraphDAO.getRecommendedTweetsForUser(userName,graphName)
        if not recommendTweets["similarTweets"].notnull().all():
            responseObject.setResponseStatus(False)
            responseObject.setResponseMessage("No Tweets")
        else:
            responseObject.setResponseStatus(True)
            responseObject.setResponseMessage("Tweets recommended")
            responseObject.setBody(json.dumps(recommendTweets.to_dict(orient='records')))

        return responseObject

    def recommendUsersForFollowing(self,userName):
        responseObject=ResponseObject()
        graphName="recommendUsersForFollowing";
        doesProjectExist=self.TwitterGraphDAO.doesGraphProjectionExist(graphName)
        if doesProjectExist:
            self.TwitterGraphDAO.dropGraphProjection(graphName)

        self.TwitterGraphDAO.createGraphProjection(graphName,self.nodes,self.weightedRelationShip)
        recommendedUsers=self.TwitterGraphDAO.recommendUsersToFollowWithinCommunity(userName)
        if not recommendedUsers["recommededUserName"].notnull().all():
            responseObject.setResponseStatus(False)
            responseObject.setResponseMessage("Could not recommend users")

        else:
            responseObject.setResponseStatus(True)
            responseObject.setResponseMessage("Users recommended")
            responseObject.setBody(recommendedUsers.to_json(orient='records'))

        return responseObject

    def identifyTopCommunities(self,number_of_communities:int):
        responseObject=ResponseObject()
        try:
            result=self.TwitterGraphDAO.identifyTopCommunitiesbySize(number_of_communities)
            responseObject.setResponseStatus(True)
            responseObject.setResponseMessage("Communities identified")
            responseObject.setBody(result.to_json(orient='records'))
        except Exception as e:
            responseObject.setResponseStatus(False)
            responseObject.setResponseMessage(f"Could not identify communities due to {e}")

        return responseObject

    def identifyMostImportantUser(self,k:int):
        responseObject=ResponseObject()
        try:
            result=self.TwitterGraphDAO.identifyMostImportantUser(k)
            responseObject.setResponseStatus(True)
            responseObject.setResponseMessage("Important users identified.")
            responseObject.setBody(result.to_json(orient='records'))
        except Exception as e:
            responseObject.setResponseStatus(False)
            responseObject.setResponseMessage(f"Could not identify important users due to {e}")

        return responseObject

    def identifyMostInfluentialUser(self,k:int):
        responseObject=ResponseObject()
        try:
            result=self.TwitterGraphDAO.identifyMostInfleuencialUser(k)
            responseObject.setResponseStatus(True)
            responseObject.setResponseMessage("Influential users identified.")
            responseObject.setBody(result.to_json(orient='records'))
        except Exception as e:
            responseObject.setResponseStatus(False)
            responseObject.setResponseMessage(f"Could not identify influential users due to {e}")

        return responseObject

    def identifyMostPopularUser(self,k:int):
        responseObject=ResponseObject()
        try:
            result=self.TwitterGraphDAO.identifyMostPopoularUser(k)
            responseObject.setResponseStatus(True)
            responseObject.setResponseMessage("Popular users identified.")
            responseObject.setBody(result.to_json(orient='records'))
        except Exception as e:
            responseObject.setResponseStatus(False)
            responseObject.setResponseMessage(f"Could not identify popular users due to {e}")

        return responseObject

    def getUsers(self,k:int, sortBy:str ):
        if sortBy.lower()=="importance":
            return self.identifyMostImportantUser(k)
        elif sortBy.lower()=="popularity":
            return self.identifyMostPopularUser(k)
        else:
            return self.identifyMostInfluentialUser(k)






if __name__=="__main__":
    connection = Neo4J().getConnection()
    twitterGraphDAO=TwitterGraphDAO(connection)
    graphService=GraphService(twitterGraphDAO)
    result=graphService.recommendTweets("rotnroll666")

    print(result)

