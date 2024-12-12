from config.Neo4J import Neo4J


class TwitterGraphDAO:
    def __init__(self,connection):
        self.connection = connection


    def createGraphProjection(self, graphName: str, nodes:list,relationships):
        query=f"""CALL gds.graph.project(
        '{graphName}',
        {nodes},
        {relationships})"""
        return self.connection.query(query).to_data_frame()

    def doesGraphProjectionExist(self, graphName:str):
        query=f"""CALL gds.graph.exists('{graphName}')
                YIELD graphName, exists
                RETURN exists"""
        df= self.connection.query(query).to_data_frame()
        return bool(df["exists"][0])

    def createGraphEmbeddingWithfastRP(self,graphName:str,property):
        query=f"""CALL gds.fastRP.mutate('{graphName}',{property})"""
        return self.connection.query(query).to_data_frame()

    def dropGraphProjection(self,graphName:str):
        query=f"""CALL gds.graph.drop('{graphName}')"""
        return self.connection.query(query).to_data_frame()

    def getRecommendedTweetsForUser(self, userName: str):
        query = f"""
        MATCH (u:User)-[:POSTS]->(t:Tweet)<-[:RETWEETS|REPLY_TO]-(s:Tweet)
        WHERE u.screen_name = '{userName}'
        WITH COLLECT(t.text) AS userTweets, COLLECT(s.text) AS seenTweets
        CALL gds.knn.stream('twitterGraph', {{
            nodeLabels: ['Tweet'],
            nodeProperties: ['embedding'],
            topK: 1
        }})
        YIELD node1, node2, similarity
        WITH node1, node2, similarity
        WHERE
            gds.util.asNode(node1).text in seenTweets AND
            NOT gds.util.asNode(node1).text IN gds.util.asNode(node2).text AND
            NOT gds.util.asNode(node2).text IN userTweets AND
            NOT gds.util.asNode(node2).text IN seenTweets
        RETURN gds.util.asNode(node1).text AS Tweet,
               COLLECT(DISTINCT gds.util.asNode(node2).text) AS similarTweets,
               COLLECT(DISTINCT similarity) AS SimilarityScores
        ORDER BY SimilarityScores DESC
        """
        df = self.connection.query(query).to_data_frame()
        return df

    def recommendUsersToFollowWithinCommunity(self, userName: str):
        query = f"""
        MATCH (targetUser:User {{name: '{userName}'}})
        WITH targetUser, targetUser.rank AS userRank, targetUser.community AS userCommunity
        MATCH (recommededUser:User {{community: userCommunity}})
        WHERE NOT (targetUser)-[:FOLLOWS]->(recommededUser) AND targetUser <> recommededUser
        RETURN recommededUser.name AS recommededUserName,
               recommededUser.screen_name AS recommededUserScreenName,
               recommededUser.pageRank AS PageRank
        ORDER BY recommededUser.pageRank DESC
        """
        df = self.connection.query(query).to_data_frame()
        return df




if __name__ == '__main__':
    connection = Neo4J().getConnection()
    # graphName="test"
    # nodes=['User', 'Tweet','Hashtag']
    # relationships=['POSTS', 'REPLY_TO', 'RETWEETS', 'MENTIONS',"TAGS"]
    # # weightedRelationShip="{INTERACTS:{orientation:'UNDIRECTED',properties:'weight'}}"
    # TwitterGraphDAO(connection).createGraphProjection(graphName,nodes,relationships)
    # embeddingProperties="{embeddingDimension:64,randomSeed:7474,mutateProperty:'embedding'}"
    # TwitterGraphDAO(connection).createGraphEmbeddingWithfastRP(graphName,embeddingProperties)
    # result = TwitterGraphDAO(connection).getRecommendedTweetsForUser("rotnroll666")
    result= TwitterGraphDAO(connection).recommendUsersToFollowWithinCommunity("MySQL")
    print(result)
    #
    # resu=TwitterGraphDAO(connection).doesGraphProjectionExist(graphName)
    # print(resu)

