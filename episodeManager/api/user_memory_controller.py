from fastapi import APIRouter
import chromadb
from model.User import User 
from model.User import Item
import embedding_model.modelUpload as modelUpload
import math
import numpy as np

client=chromadb.PersistentClient()

embed_model=modelUpload.model_upload()

userRouter = APIRouter()

@userRouter.post("/user/make/collection")
async def make_collection(user: User):
    client.create_collection(name=user.userId+"_episode", metadata={"hnsw:space":"cosine"})
    client.create_collection(name=user.userId+"_buffer", metadata={"hnsw:space":"cosine"})
    return 200; 

@userRouter.post("/user/query")
async def get_user_memory(item : Item):
    userId = item.userId
    observation = item.observation
    contextValid = item.contextValid
    importance = item.importance
    query = item.query
    collection=client.get_collection(name=userId)
    
    #마지막 기억의 시나리오 id 확인하기
    scenarioId = get_last_sceneId(collection)
        
    #문맥이 유효한지 확인
    if(not contextValid):
        scenarioId = str(int(scenarioId) + 1)
    
    #데이터 정리
    if(collection.count()!=0):
        id=str(get_ids_max(collection)+1)
    else:
        id=str(1)
    
    metadatas=[
        {"id": id, "userId":userId,"scenarioId":scenarioId,"importance":importance, "observation" : observation}
    ]
    
    embedding_word = [observation]
    embeddings = embed_model.encode(embedding_word)
    embeddings = embeddings.tolist()
    
    #데이터 삽입
    collection.add(
        ids=id,
        metadatas=metadatas,
        embeddings=embeddings
    )
    
    #쿼리 날리기
    result = query_vector_db(collection,query)

    if(result!=410):
    #답변 필터링
        result_list = (result["metadatas"])[0] #유사도 순서대로 정렬된 데이터
        
        result_list = filter_by_importance(result_list)
        
        result_list = filter_by_id(result_list)
        
        #같은 시나리오 전부 가져오기
        
        return result_list
    
    return 
    
    
def filter_by_importance(result_list):
    # importances=[0.1,0.1,0.99,0.98,0.97,0.95,0.89,0.99] #Test
    importances=[]
    valid_list=[]
    for item in result_list:
        importances.append(item['importance'])
    Q1,Q3=map(float , np.percentile(importances,[25,75]))
    IQR=Q3-Q1
    standard_line=Q1-IQR*1.5
    for item in result_list:
        if(item['importance']>standard_line):
            valid_list.append(item)
    return valid_list
    
def filter_by_id(result_list):
    result_list=sorted(result_list, key=lambda x: int(x["id"]),reverse=True)
    return result_list

def query_vector_db(collection,query):
    n_result = collection.count()
    if(n_result==0):
        return 410
    elif(n_result==1):
        n_result=1
    else:
        n_result=int(math.log2(n_result))
    query_embedding_word=[query]
    query_embedding = embed_model.encode(query_embedding_word)
    query_embedding=query_embedding.tolist()
    
    result=collection.query(
        query_embeddings=query_embedding[0],
        n_results=n_result,
    )
    
    return result


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