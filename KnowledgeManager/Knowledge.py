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
# server_type = os.getenv('servertype')

communitys=[]

# if(server_type=="dev"):
    # Neo4j에 연결하기 위한 드라이버 설정 (dev)
# uri = "bolt://localhost:7687"  # 기본적으로 Neo4j는 이 포트를 사용
# username = neo4juser
# password = neo4jpassword
# else:
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

    community_local=[]

    query='''
    MATCH (w:Word)  // 'Word' 레이블을 가진 노드와 매칭
    RETURN id(w) AS nodeId, w.community_id As community_id , w.embedding AS embedding
    ORDER BY community_id, nodeId
    '''
    result = tx.run(query)
    for record in result:
        node_id=record["nodeId"]
        community_id=record['community_id']
        embedding=record['embedding']
        for community in community_local:
            isExist=False
            if(community["id"]==community_id):
                #있으면 해야 할 것들
                isExist=True
                community["node"].append(node_id)
                for i in range(len(community["embedding"])):
                    community["embedding"][i]+=embedding[i]
        if(len(community_local)==0 or not isExist):
            community_local.append({"id":community_id,"node":[node_id],"embedding":embedding})

    for item in community_local:
        for i in range(len(item["embedding"])):
            item["embedding"][i]/=len(item["node"])

    for i in range(len(community_local)):
        print(str(community_local[i]["id"])+"번 커뮤니티 노드 번호: " + str(community_local[i]["node"]))

    global communitys
    communitys=community_local
    return
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

    # 커뮤니티 탐지
    with driver.session() as session:
        session.execute_write(community_detect)

    # 드라이버 종료
    driver.close()

    return

def getMemoryByKnowlegeGraph(query):

    driver = GraphDatabase.driver(uri, auth=(username, password))

    word=[query]
    word_embedding = embed_model.encode(word)
    word_embedding=(word_embedding.tolist())[0]

    cosine_compare_list=[]
    max_idx=0
    max_cosine=0.0
    for i in range(len(communitys)):
        community_embedding=communitys[i]["embedding"]
        cosine=calculate_cosine_distance(community_embedding,word_embedding)
        cosine_compare_list.append({"communityId":communitys[i]["id"],"cosine":cosine})

    cosine_compare_list.sort(key=lambda x:-x["cosine"])

    #print("비슷한 커뮤니티")
    #print(similar_community)

    node_result=[]
    episodeIdList=[]

    for i in range(len(cosine_compare_list)//8):
        community_id=cosine_compare_list[i]["communityId"]
        for j in range(len(communitys)):
            if(community_id==communitys[j]["id"]):
                similar_community=communitys[j]
                break

        for i in range(len(similar_community["node"])):
            nodeId=similar_community["node"][i]
            with driver.session() as session:
                query='''
                    MATCH (n)-[r]->(m)
                    WHERE id(n) = $nodeId
                    RETURN n, m, r
                '''
                result=session.run(query,nodeId=nodeId)
                for record in result:
                    episodeIdList.append(record["r"]["episodeId"])
                    node_result.append(record["n"]["name"]+" "+record["m"]["name"]+" "+record["r"]["relationship"])

        #없으면 반대로
        if(len(node_result)==0):
            with driver.session() as session:
                query='''
                    MATCH (n)-[r]-(m)
                    WHERE id(n) = $nodeId
                    RETURN n, m, r
                '''
                result=session.run(query,nodeId=nodeId)
                for record in result:
                    episodeIdList.append(record["r"]["episodeId"])
                    node_result.append(record["m"]["name"]+" "+record["n"]["name"]+" "+record["r"]["relationship"])

    episodeIdList=list(set(episodeIdList))
    return node_result,episodeIdList


driver = GraphDatabase.driver(uri, auth=(username, password))
with driver.session() as session:
    session.execute_write(community_detect)

# 드라이버 종료
driver.close()

