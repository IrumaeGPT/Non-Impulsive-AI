'''
1. Episode Memory 에서 해당 episode id 에 해당하는 기억 가지고 오기
2. 기억 추가하기 

'''

from fastapi import APIRouter
import chromadb
from model.episodeItem import episodeItem
import embedding_model.modelUpload as modelUpload

client=chromadb.PersistentClient()

embed_model=modelUpload.model_upload()

episodeRouter = APIRouter()

@episodeRouter.post("/episode/add")
async def addEpisodeMemory(episodeItem: episodeItem):
    if(episodeItem.isContextSwitched):
        k=3    #문맥 변환, 그래프 및 DB 업데이트
    userId = episodeItem.userId
    observation = episodeItem.observation
    episodeId = episodeItem.episodeId
    
    collection=client.get_collection(name=userId)
    
    if(collection.count()!=0):
        id=str(get_ids_max(collection)+1)
    else:
        id=str(1)
        
    metadatas=[
        {"id": id, "userId":userId,"episodeId":episodeId,"observation" : observation}
    ]
    
    embedding_word = [" "]
    embeddings = embed_model.encode(embedding_word)
    embeddings = embeddings.tolist()
     
    collection.add(
        ids=id,
        metadatas=metadatas,
        embeddings=embeddings
    )
    
    return metadatas
    
@episodeRouter.get("/episode/get/{userId}/{episodeId}")
async def getEpisodeById(episodeId : int, userId : str):
    episodeMemory=[]
    
    collection=client.get_collection(name=userId)
    
    result = query_vector_db(collection," ")
    metadatas=(result["metadatas"])[0]
    
    for i in range(len(metadatas)):
        if(int((metadatas[i])["episodeId"])==episodeId):
            episodeMemory.append(metadatas[i])
            
    return episodeMemory
    
def query_vector_db(collection,query):
    n_result = collection.count()
    if(n_result==0):
        return 410
    elif(n_result==1):
        n_result=1
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