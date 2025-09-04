import json
from flask import Flask,request, jsonify
from flask_cors import CORS

from ProjectInit import ProjectInit
from config.Neo4J import Neo4J
from dto.ResponseObject import ResponseObject
from repository.TwitterGraphRepository import TwitterGraphDAO
from service.GraphService import GraphService
app = Flask(__name__)
CORS(app)
neo4J=Neo4J()
twitterGraphDAO=TwitterGraphDAO(neo4J.getConnection())
graphService=GraphService(twitterGraphDAO)
ProjectInit(TwitterGraphDAO(neo4J.getConnection())).data_preparation()

@app.route('/recommendTweetsToUser', methods=['POST'])
def recommendTweetsToUser():
    responseObject=ResponseObject()
    inputData = request.get_json()
    user= inputData.get('userName', 'rotnroll666')
    try:
        result=graphService.recommendTweets(user)
        return jsonify(result.jsonfyResponse())
    except Exception as e:
        responseObject.setResponseStatus(False)
        responseObject.setResponseMessage("Could not process the request. Please try again later.")
        return jsonify(responseObject.jsonfyResponse())
@app.route('/recommendUser', methods=['POST'])
def recommendUsersForFollowing():
    responseObject=ResponseObject()
    inputData = request.get_json()
    user= inputData.get('userName', 'MySQL')
    try:
        result=graphService.recommendUsersForFollowing(user)
        return jsonify(result.jsonfyResponse())
    except Exception as e:
        responseObject.setResponseStatus(False)
        responseObject.setResponseMessage("Could not process the request. Please try again later.")
        return jsonify(responseObject.jsonfyResponse())

@app.route('/communities', methods=['GET'])
def getCommunities():
    responseObject = ResponseObject()
    number_of_communities=request.args.get('number_of_communities',10)
    try:
        result= graphService.identifyTopCommunities(number_of_communities)
        return jsonify(result.jsonfyResponse())
    except Exception as e:
        responseObject.setResponseStatus(False)
        responseObject.setResponseMessage("Could not process the request. Please try again later.")
        return jsonify(responseObject.jsonfyResponse())

@app.route('/user', methods=['GET'])
def getUser():
    sortBy = request.args.get('sort', 'influence')
    responseObject = ResponseObject()
    limit = request.args.get('limit', 10)
    try:
        result = graphService.getUsers(limit, sortBy)
        return jsonify(result.jsonfyResponse())
    except Exception as e:
        responseObject.setResponseStatus(False)
        responseObject.setResponseMessage("Could not process the request. Please try again later.")
        return jsonify(responseObject.jsonfyResponse())




if __name__ == '__main__':
    app.run(debug=True)
