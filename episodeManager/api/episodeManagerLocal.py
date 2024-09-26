import chromadb
from ..model.episodeItem import episodeItem
from ..model.queryItem import queryItem
from ..model.updateEpisodeItem import updateEpisodeItem
from ..embedding_model import modelUpload as modelUpload
import numpy as np
from sklearn.cluster import KMeans

client=chromadb.PersistentClient()

embed_model=modelUpload.model_upload()

cluster = []

def make_collection(userId):
    print(userId)
    print(client)
    client.create_collection(name=userId+"_episode", metadata={"hnsw:space":"cosine","hnsw:M": 1024})
    client.create_collection(name=userId+"_buffer", metadata={"hnsw:space":"cosine","hnsw:M": 1024})
    print("Sucess")
    return 200; 

def updateCluster(cluster_result, embeddings):
    global cluster
    cluster = [{"clusterId":0, "sum": [0 for _ in range(768)],"count":0, "avg":[0 for _ in range(768)]}]
    for idx in range(len(cluster_result)):
        isExist=False
        for i in range(len(cluster)):
            if((cluster[i])["clusterId"]==cluster_result[idx]):
                isExist=True
                for j in range(768):
                    ((cluster[i])["sum"])[j]+=(embeddings[idx])[j]
                (cluster[i])["count"]+=1
                break
            else:
                continue
        if(not isExist):
            cluster.append({"clusterId":cluster_result[idx], "sum": embeddings[idx] , "count":1 ,"avg": [0 for _ in range(768)]})
    
    for idx in range(len(cluster)):
        for j in range(768):
            ((cluster[idx])["avg"])[j] = ((cluster[idx])["sum"])[j] / ((cluster[idx])["count"])
    
    return
            
def saveQueryInShortTermMemory(userId, observation):
    collection=client.get_collection(name=userId+"_buffer")
    n_result = collection.count()
    if(collection.count()!=0):
        id=str(get_ids_max(collection)+1)
    else:
        id=str(1)
        
    metadatas=[
        {"id": id, "userId":userId, "observation" : observation}
    ]
    
    embeddings = [[0 for _ in range(768)]]
    
    collection.add(
        ids=id,
        metadatas=metadatas,
        embeddings=embeddings
    )
    
    query_embedding_word=[" "]
    query_embedding = embed_model.encode(query_embedding_word)
    query_embedding=query_embedding.tolist()
    
    result=collection.query(
        query_embeddings=query_embedding[0],
        n_results=n_result+1,
    )
    
    for i in range(len((result["metadatas"])[0])):
        if ((result["metadatas"])[0])[i] is None:
            print("None deceted")
            collection.delete(ids=[((result["ids"])[0])[i]])
        
    # print("들어간거 확인")
    # print((result["metadatas"])[0])
    return metadatas


def getShortTermMemories(userId):
    collection=client.get_collection(name=userId+"_buffer")
    n_result = collection.count()
    resultString=""
    
    if(n_result==0):
        return []
    elif(n_result==1):
        n_result=1
        
    query_embedding_word=[" "]
    query_embedding = embed_model.encode(query_embedding_word)
    query_embedding=query_embedding.tolist()
    
    result=collection.query(
        query_embeddings=query_embedding[0],
        n_results=n_result,
    )
    
    metadatas = (result["metadatas"])[0]
    print("메타 데이터들: ")
    print(metadatas)
    
    if(not None in metadatas):
        metadatas.sort(key=lambda x: int(x["id"]))
        for item in metadatas:
            resultString+=(item["observation"])
            resultString+="\n" 
        
    print(resultString)
    
    return resultString
    

def updateEpisodeMemory(userId, summary):
    epiosdeEmbedding=[]

    collection=client.get_collection(name=userId+"_episode")
    collection_buffer = client.get_collection(name=userId+"_buffer")
    #Episode 다 빼고
    n_result = collection.count()
    if(n_result==0):
        #최초 클러스터 형성하기
        print("Hello")
        id=str(1)
        
        metadatas=[
            {"id": id, "userId":userId, "summary" : summary, "cluster": 0 }
        ]
        
        summary_embedding_word=[summary]
        summary_embedding = embed_model.encode(summary_embedding_word)
        summary_embedding=summary_embedding.tolist()
        
        collection.add(
            ids=id,
            metadatas=metadatas,
            embeddings=summary_embedding
        )
        
        updateCluster([0], summary_embedding)
    
        delete_buffer_memory(collection_buffer)
        return 
    
    query_embedding_word=[" "]
    query_embedding = embed_model.encode(query_embedding_word)
    query_embedding=query_embedding.tolist()
    
    result=collection.query(
        query_embeddings=query_embedding[0],
        n_results=n_result,
    )
    
    metas=(result["metadatas"])[0]
    metas.sort(key= lambda x: int(x["id"]))
    
    for item in metas:
        item_embedding = embed_model.encode([item["summary"]])
        item_embedding = item_embedding.tolist()
        epiosdeEmbedding.append(item_embedding[0])
    
    summary_embedding_word=[summary]
    summary_embedding = embed_model.encode(summary_embedding_word)
    summary_embedding=summary_embedding.tolist()
    epiosdeEmbedding.append(summary_embedding[0])
    
    # K-Means 클러스터링
    k = 2  # 클러스터 개수
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(epiosdeEmbedding)

    # 클러스터 레이블과 중심점
    cluster_labels = kmeans.labels_
    print(cluster_labels)
    
    for idx in range(0,len(metas)):
        if(cluster_labels[idx]!=(metas[idx])["cluster"]):
            collection.delete(ids=[(metas[idx])["id"]])
            
            updated_metadata = {"id": (metas[idx])["id"], "userId": (metas[idx])["userId"], "summary" : (metas[idx])["summary"], "cluster": int(cluster_labels[idx]) }

            collection.add(
                ids=(metas[idx])["id"],  # 새로운 ID
                embeddings=epiosdeEmbedding[idx],  # 예시 벡터
                metadatas=updated_metadata  # 수정된 메타데이터 사용
            )
    
    id=str(get_ids_max(collection)+1)
    
    metadatas=[
            {"id": id, "userId":userId, "summary" : summary, "cluster": int(cluster_labels[-1])}
    ]
    
    result = collection.add(
        ids=id,
        metadatas=metadatas,
        embeddings=summary_embedding
    )
    
    result = collection.query(
        query_embeddings=query_embedding[0],
        n_results=n_result+1
    )
    
    updateCluster(cluster_labels , epiosdeEmbedding)
    
    delete_buffer_memory(collection_buffer)
    #클러스터링 하고
    #클러스터 번호 업데이트

    return (result["metadatas"])[0]

def delete_buffer_memory(collection):
    ids=[]
    for i in range(1,get_ids_max(collection)+1):
        ids.append(str(i))
    print("버퍼 삭제 리스트:")
    print(ids)
    collection.delete(ids=ids)
    return

def retrieveEpisodes(userId,query):
#     episodeMemory=[]
    
#     collection=client.get_collection(name=userId)
    
#     result = query_vector_db(collection," ")
#     metadatas=(result["metadatas"])[0]
    
#     for i in range(len(metadatas)):
#         if(int((metadatas[i])["episodeId"])==episodeId):
#             episodeMemory.append(metadatas[i])
            
#     return episodeMemory
    
# def query_vector_db(collection,query):
#     n_result = collection.count()
#     if(n_result==0):
#         return 410
#     elif(n_result==1):
#         n_result=1
#     query_embedding_word=[query]
#     query_embedding = embed_model.encode(query_embedding_word)
#     query_embedding=query_embedding.tolist()
    
#     result=collection.query(
#         query_embeddings=query_embedding[0],
#         n_results=n_result,
#     )
    
    
    ## 버전 2
    collection=client.get_collection(name=userId+"_episode")
    n_result = collection.count()
    result_response=[]
    
    query_word=[query]
    query_word_embedding = embed_model.encode(query_word)
    query_word_embedding = query_word_embedding.tolist()
    cosine_result = []
    
    for i in range(len(cluster)):
        cluster_avg = (cluster[i])["avg"]
        cosine_result.append([(cluster[i]["clusterId"]),cosine_similarity(query_word_embedding[0],cluster_avg)])
    cosine_result.sort(key=lambda x: x[1], reverse=True)
    
    print(cosine_result)
    max_cluster = (cosine_result[0])[0]
    
    query_embedding_word=[" "]
    query_embedding = embed_model.encode(query_embedding_word)
    query_embedding=query_embedding.tolist()
    
    result=collection.query(
        query_embeddings=query_embedding[0],
        n_results=n_result,
    )
    
    metas=(result["metadatas"])[0]
    
    for item in metas:
        if(item["cluster"]==max_cluster):
            result_response.append(item["summary"])
    
    return result_response

def getEpisodesMemory(userId):
    collection=client.get_collection(name=userId+"_episode")
    n_result = collection.count()
    query_embedding_word=[" "]
    query_embedding = embed_model.encode(query_embedding_word)
    query_embedding=query_embedding.tolist()
    
    result=collection.query(
        query_embeddings=query_embedding[0],
        n_results=n_result,
    )
    
    metadatas = (result["metadatas"])[0]
    print("메타 데이터들: ")
    print(metadatas)
    metadatas.sort(key=lambda x: int(x["id"]))
    
    return metadatas
    

def cosine_similarity(list1, list2):
    # 리스트를 numpy 배열로 변환
    vec1 = np.array(list1)
    vec2 = np.array(list2)
    
    # 두 벡터의 내적 계산
    dot_product = np.dot(vec1, vec2)
    
    # 벡터의 크기(노름) 계산
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    # 코사인 유사도 계산
    cosine_sim = dot_product / (norm_vec1 * norm_vec2)
    
    return cosine_sim

    #id 최대값을 int로 반환
def get_ids_max(collection):
    n_result=collection.count()
    query_embedding_word=[" "] #바꿔야 하는 부분
    query_embedding=embed_model.encode(query_embedding_word)
    query_embedding=query_embedding.tolist()
    result=collection.query(
            query_embeddings=query_embedding[0],
            n_results=n_result
    )
    result_ids=(result["ids"])[0]
    id_int=[]
    for j in range(0,len(result_ids)):
        id_int.append(int(result_ids[j]))
    return max(id_int)

def get_last_sceneId(collection):
    n_result=collection.count()
    if(n_result!=0):
        ids=[str(get_ids_max(collection))]
        result=collection.get(ids=ids)
        scenarioId = ((result["metadatas"])[0])['scenarioId']
        return scenarioId
    return "0"