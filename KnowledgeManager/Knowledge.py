from neo4j import GraphDatabase
import numpy as np
from KnowledgeManager.embedding_model.modelUpload import model_upload
import os
from dotenv import load_dotenv

current_directory = os.path.dirname(os.path.abspath(__file__))

load_dotenv(dotenv_path=current_directory+"/../episodeManager/.env")

host = os.getenv('host')
neo4juser = os.getenv('neo4juser')
neo4jpassword = os.getenv('neo4jpassword')
server_type = os.getenv('servertype')

if(server_type=="dev"):
    # Neo4j에 연결하기 위한 드라이버 설정 (dev)
    uri = "bolt://localhost:7687"  # 기본적으로 Neo4j는 이 포트를 사용
    username = neo4juser
    password = neo4jpassword
else:
    # Neo4j에 연결하기 위한 드라이버 설정 (local)
    uri = "bolt://localhost:7687"  # 기본적으로 Neo4j는 이 포트를 사용
    username = "neo4j"
    password = "mustrelease1234"

#embedding model
embed_model=model_upload()

# driver = GraphDatabase.driver(uri, auth=(username, password))

# 노드 생성 함수

def create_node(tx, word, embedding):
    query = """
    MERGE (p:Word {name: $word})
    ON CREATE SET p.embedding = $embedding
    """
    tx.run(query, word=word, embedding=embedding)

    return
    # query = """
    # MERGE (p:Word {name: $word, embedding: $embedding})
    # """
    # tx.run(query, word=word, embedding=embedding)

    # query = """
    # MERGE (p:distance_graph {name: $word, embedding: $embedding})
    # """
    # tx.run(query, word=word, embedding=embedding)

# 관계 생성 함수
def create_relationship(tx, fromWord, toWord, relationship, episodeId):
    query = """
    MATCH (w1:Word {name: $fromWord}), (w2:Word {name: $toWord})
    MERGE (w1)-[r:relation {relationship: $relationship , episodeId: $episodeId}]->(w2)
    SET r.distance = 1
    """
    tx.run(query, fromWord=fromWord, toWord=toWord,relationship=relationship, episodeId=episodeId)

# 노드를 삭제하는 함수
def delete_node(tx, word):
    query = f"""
    MATCH (n:Word {{name: $word}})
    DETACH DELETE n
    """
    tx.run(query, word=word)

def community_detect(tx):
    # create_similarity(tx)

    query='''
        CALL gds.graph.exists('embedding-similarity-graph')
        YIELD graphName, exists
        RETURN graphName, exists
    '''

    result=tx.run(query)
    for records in result:
        if(records["exists"]):
            query="CALL gds.graph.drop('embedding-similarity-graph')"
            tx.run(query)

    query='''
    CALL gds.graph.project(
        'embedding-similarity-graph',
        ['Word'],
        {
            relation: {
                properties: 'distance'
            }
        }
    ) YIELD graphName, nodeCount, relationshipCount  // YIELD 추가

    CALL gds.louvain.stream('embedding-similarity-graph')
    YIELD nodeId, communityId
    RETURN id(gds.util.asNode(nodeId)) AS nodeId, communityId
    ORDER BY communityId, nodeId
    '''

    result=tx.run(query)
    for record in result:
        print(record["nodeId"],record["communityId"])
        query='''
            MATCH (n)
            WHERE id(n) = $nodeId
            SET n.community_id = $communityId
        '''
        tx.run(query,nodeId=record["nodeId"],communityId=record["communityId"])

    # N번 노드 속성에 community 부여하기

def create_similarity(tx):
    query = "MATCH (w:distance_graph) RETURN id(w) AS id, w.embedding AS embedding"

    result = tx.run(query)
    words = [(record["id"], record["embedding"]) for record in result]

    for i, (id_a, embedding_a) in enumerate(words):
        for id_b, embedding_b in words[i+1:]:
            distance = calculate_cosine_distance(embedding_a, embedding_b)
            print(distance)
            print(id_a)
            print(id_b)

            if(distance>0.5):
                tx.run(
                    """
                    MATCH (a:distance_graph), (b:distance_graph)
                    WHERE id(a)=$id_a and id(b)=$id_b
                    MERGE (a)-[r:relation]->(b)
                    SET r.distance = $distance
                    """,
                    id_a=id_a, id_b=id_b, distance=distance
                )

def calculate_cosine_distance(vec1, vec2):
    """
    두 벡터 간 코사인 거리를 계산하는 함수
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    cosine_similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    return cosine_similarity

def updateKnowledgeGraph(relationTuples,sourceEpisodeId):

    driver = GraphDatabase.driver(uri, auth=(username, password))

    #커뮤니티 노드 간선 생성
    for relation in relationTuples:
        if None in relation:
            print(relation)
            continue

        word=[relation[0],relation[2]]
        edge = relation[1]
        word_embedding = embed_model.encode(word)
        word_embedding=word_embedding.tolist()

        with driver.session() as session:
            session.execute_write(create_node,word[0],word_embedding[0])
            session.execute_write(create_node,word[1],word_embedding[1])
            session.execute_write(create_relationship,word[0],word[1],edge,sourceEpisodeId)

    #커뮤니티 탐지
    #session.execute_write(community_detect)

    # 드라이버 종료
    driver.close()

    return

driver = GraphDatabase.driver(uri, auth=(username, password))
with driver.session() as session:
    session.execute_write(community_detect)
# 드라이버 종료
driver.close()

