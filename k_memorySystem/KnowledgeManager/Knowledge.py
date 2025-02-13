import numpy as np
from KnowledgeManager.embedding_model.modelUpload import model_upload
import os
from dotenv import load_dotenv
from sklearn.cluster import KMeans
import numpy as np
import math
from globals.util import Neo4jUtil as Neo4jUtil

#embedding model
embed_model=model_upload()

driver = Neo4jUtil.driver

# 노드 생성 함수
def create_node(tx, word, embedding):
    query = """
    MERGE (p:Word {name: $word})
    ON CREATE SET p.embedding = $embedding
    """
    tx.run(query, word=word, embedding=embedding)
    return

# 관계 생성 함수
def create_relationship(tx, fromWord, toWord, relationship, episodeId):
    query = """
    MATCH (w1:Word {name: $fromWord}), (w2:Word {name: $toWord})
    MERGE (w1)-[r:relation {relationship: $relationship , episodeId: $episodeId}]->(w2)
    SET r.distance = 1
    """
    tx.run(query, fromWord=fromWord, toWord=toWord,relationship=relationship, episodeId=episodeId)

# 노드를 삭제하는 함수
# def delete_node(tx, word):
#     query = f"""
#     MATCH (n:Word {{name: $word}})
#     DETACH DELETE n
#     """
#     tx.run(query, word=word)

# 커뮤니티 감지
def community_detect(tx):
    community_local=[]

    query='''
    MATCH (w:Word)  // 'Word' 레이블을 가진 노드와 매칭
    RETURN id(w) AS nodeId, w.embedding AS embedding
    ORDER BY nodeId
    '''
    result = tx.run(query)

    data = []
    for record in result:
        node_id=record["nodeId"]
        embedding=record['embedding']
        data.append({"nodeId":node_id,"embedding":embedding})

    embeddings = np.array([item["embedding"] for item in data])

    global kmeans
    kmeans = KMeans(n_clusters=int(math.log2(len(data))),random_state=0)
    kmeans.fit(embeddings)

    for i, item in enumerate(data):
        item["community_id"] = int(kmeans.labels_[i])

    for record in data:
        node_id=record["nodeId"]
        community_id=record['community_id']
        embedding=record['embedding']
        isExist=False
        for community in community_local:
            if(community["id"]==community_id):
                #있으면 해야 할 것들
                isExist=True
                community["node"].append(node_id)
                
        if(len(community_local)==0 or not isExist):
            community_local.append({"id":community_id,"node":[node_id]})

    community_local.sort(key=lambda x: x["id"])

    for i in range(len(community_local)):
        print(str(community_local[i]["id"])+"번 커뮤니티 노드 번호: " + str(community_local[i]["node"]))

    global communitys
    communitys=community_local
    
    return

# 지식 그래프 업데이트
def updateKnowledgeGraph(relationTuples,sourceEpisodeId):
    # driver = GraphDatabase.driver(uri, auth=(username, password))
    print("Hello")
    #커뮤니티 노드 간선 생성
    for relation in relationTuples:
        if None in relation:
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

    return

# 지식 그래프 가져오기
def getMemoryByKnowlegeGraph(query):
    global kmeans

    word=[query]
    word_embedding = embed_model.encode(word)
    word_embedding=(word_embedding.tolist())[0]
    word_embedding_2D = [word_embedding]

    similar_community_id = (kmeans.predict(np.array(word_embedding_2D)))[0]

    node_result=[]
    episodeIdList=[]

    similar_community = communitys[similar_community_id]

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

##최초 한번 실행
with driver.session() as session:
    session.execute_write(community_detect)
driver.close()
