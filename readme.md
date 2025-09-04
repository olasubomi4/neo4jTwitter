
# Twitter Recommendation System

A graph-powered recommendation engine built with Neo4j, Flask, and Streamlit that:

1. Recommends tweets to users based on interactions and interests.
2. Recommends people to follow to foster engagement and network growth.

The system enriches the original Twitter graph with an INTERACTS relationship and user-level features (popularity, importance, influence) so that Graph Data Science (GDS) algorithms can generate relevant recommendations.


## Table of Contents

1. Overview
2. Data Source
3. How It Works
4. Environment Variables
5. Quickstart
6. Run
7. Contact



### Overview

Twitter, as a social media platform, relies heavily on user interaction for sustained growth. By leveraging graph-based algorithms, this project aims to:

1. Identify influential and popular users in the network.
2. Create communities based on user interactions.
3. Suggest tweets and followers using graph embeddings and similarity measures.

### Data Source

The dataset comes from the Neo4j Graph Examples – Twitter v2 project:


GitHub: https://github.com/neo4j-graph-examples/twitter-v2

During the data understanding phase, the dataset was found to be one-sided (i.e., lacking bidirectional interactions between users). Many GDS algorithms depend on explicit user interactions, so this project introduces a derived relationship:

INTERACTS — created from available relationships among other nodes to better reflect user-to-user engagement.

Additionally, the data preparation step adds user features:

1. Popularity score
2. Importance score
3. Influence score

These features help downstream tasks such as ranking and personalised recommendations.

### How It Works

When the environment variable IS_FIRST_TIME_USER is set to True, the data preparation pipeline runs automatically:

1. Generates the INTERACTS relationships.
2. Computes feature engineering for each user (popularity, importance, influence).
3. Once prepared, the Flask API serves recommendation endpoints, and the Streamlit app provides a simple UI to explore results.

### Environment Variables

Create a .env file in the project root with the following content (sample):


    NEO4J_USER=neo4j 
    
    NEO4J_PASS=password
    
    NEO4J_HOST=bolt://localhost:7687
    
    API_BASE_URL=http://127.0.0.1:5000
    
    IS_FIRST_TIME_USER=True

Field explanations

NEO4J_USER – Username for your Neo4j database.

NEO4J_PASS – Password for your Neo4j database.

NEO4J_HOST – Connection URI for Neo4j.

API_BASE_URL – The base URL for the Flask API (where your backend serves endpoints).

IS_FIRST_TIME_USER – If True, runs the bootstrap step to generate INTERACTS and compute features. Set it back to False after the first run to skip re-computation.


### Quickstart

1) Prerequisites:
   Python 3.9+ (recommended)
   A running Neo4j instance (local or Sandbox)
   Neo4j GDS library installed on the server for advanced algorithms (for local db instances)

2) Setup the Twitter Neo4j Database

    Follow the steps in the official dataset repo:
    https://github.com/neo4j-graph-examples/twitter-v2

3) Install Dependencies

    pip install -r requirements.txt 

4) Configure Environment

    Create .env using the template above. For the very first data prep run:

    IS_FIRST_TIME_USER=True 

###  Run
    
1. Start the Flask API `flask --app app run`
2. Start the Streamlit App In another terminal: `streamlit run streamlit_app.py` 
3. After the first successful data preparation, consider setting IS_FIRST_TIME_USER=False in your .env to speed up subsequent runs.

### Contact

For questions or partnership opportunities, please reach out:  [olasubomiodekunle@gmail.com]()

![Screenshot 2025-09-04 at 17.53.34.png](neo4j_demo_images/Screenshot%202025-09-04%20at%2017.53.34.png)
![Screenshot 2025-09-04 at 17.53.53.png](neo4j_demo_images/Screenshot%202025-09-04%20at%2017.53.53.png)
![Screenshot 2025-09-04 at 17.54.10.png](neo4j_demo_images/Screenshot%202025-09-04%20at%2017.54.10.png)
![Screenshot 2025-09-04 at 17.54.13.png](neo4j_demo_images/Screenshot%202025-09-04%20at%2017.54.13.png)
![Screenshot 2025-09-04 at 17.54.28.png](neo4j_demo_images/Screenshot%202025-09-04%20at%2017.54.28.png)
![Screenshot 2025-09-04 at 17.54.50.png](neo4j_demo_images/Screenshot%202025-09-04%20at%2017.54.50.png)