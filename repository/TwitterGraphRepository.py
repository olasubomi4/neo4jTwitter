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

    def getRecommendedTweetsForUser(self, userName: str, graphName: str):
        query = f"""
        MATCH (u:User)-[:POSTS]->(t:Tweet)<-[:RETWEETS|REPLY_TO]-(s:Tweet)
        WHERE u.screen_name = '{userName}'
        WITH COLLECT(t.text) AS userTweets, COLLECT(s.text) AS seenTweets
        CALL gds.knn.stream('{graphName}', {{
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

    def identifyTopCommunitiesbySize(self,number_of_communities:int):
        query = f"""
            MATCH (u:User)
            RETURN u.community AS communityId, collect(u.screen_name) AS members
            ORDER BY size(members) DESC limit {number_of_communities}
        """
        df = self.connection.query(query).to_data_frame()
        return df

    def identifyMostPopoularUser(self,size:int):
        query = f"""
            MATCH (u:User)
            RETURN u.name AS userName, u.popularity AS score
            ORDER BY score DESC limit {size}
        """
        df = self.connection.query(query).to_data_frame()
        return df

    def identifyMostImportantUser(self,size:int):
        query = f"""
            MATCH (u:User)
            RETURN u.name AS userName, u.influence AS score
            ORDER BY score DESC limit {size}
        """
        df = self.connection.query(query).to_data_frame()
        return df

    def identifyMostInfleuencialUser(self,size:int):
        query = f"""
            MATCH (u:User)
            RETURN u.name AS userName, u.pageRank AS score
            ORDER BY score DESC limit {size}
        """
        df = self.connection.query(query).to_data_frame()
        return df


    def createInteractsRelationship(self):
        query = f"""
        MATCH (u1:User)-[:POSTS]->(t:Tweet)<-[:REPLY_TO|RETWEETS]-(t2)<-[:POSTS]-(u2:User)
        WHERE t2:Tweet OR t2:Retweet
        MERGE (u2)-[r:INTERACTS]->(u1)
        ON CREATE SET r.weight = 1
        ON MATCH SET r.weight = r.weight + 1
        
        UNION
        
        MATCH (u1:User)<-[:MENTIONS]-(t:Tweet)<-[:REPLY_TO|RETWEETS]-(t2)<-[:POSTS]-(u2:User)
        WHERE t2:Tweet OR t2:Retweet
        MERGE (u2)-[r:INTERACTS]->(u1)
        ON CREATE SET r.weight = 1
        ON MATCH SET r.weight = r.weight + 1
        
        UNION
        
        MATCH (u1:User)<-[:MENTIONS]-(t:Tweet)<-[:POSTS]-(u2:User)
        MERGE (u2)-[r:INTERACTS]->(u1)
        ON CREATE SET r.weight = 1
        ON MATCH SET r.weight = r.weight + 1
        """
        return self.writeQuery(query)

    def writeQuery(self,query):
        tx = self.connection.begin()
        try:
            cursor = tx.run(query)
            tx.commit()
            return cursor.to_data_frame()
        except Exception:
            tx.rollback()
            raise

    def writePageRankResult(self,graphName:str):
        query=f"""call gds.pageRank.write('{graphName}',{{writeProperty:"pageRank"}})"""
        return self.writeQuery(query)
    def writeDegreeResult(self,graphName:str):
        query=f"""call gds.degree.write('{graphName}',{{writeProperty:"popularity"}})"""
        return self.writeQuery(query)
    def writeCommunityResult(self,graphName:str):
        query=f"""call gds.labelPropagation.write('{graphName}',{{relationShipWeightProperty:"weight",maxIterations:1,writeProperty:"community"}})"""
        return self.writeQuery(query)
    def writeBetweennessResult(self,graphName:str):
        query = f"""call gds.betweenness.write('{graphName}',{{writeProperty:"influence"}})"""
        return self.writeQuery(query)


if __name__ == '__main__':
    connection = Neo4J().getConnection()
    # result= TwitterGraphDAO(connection).recommendUsersToFollowWithinCommunity("MySQL")
    # print(result)
    #
    # resu=TwitterGraphDAO(connection).doesGraphProjectionExist("weightGraph")
    # print(resu)

