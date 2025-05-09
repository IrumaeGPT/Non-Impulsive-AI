from fastapi import FastAPI
from k_memorySystem.LLMController import LLMController
from k_memorySystem.episodeManager import episodeManager as episodeManager
from chatingManaher import ChatingManager as ChatingManager
from k_memorySystem.KnowledgeManager import Knowledge as knowledgeManager
from pydantic import BaseModel
from AuthManager.controller import AuthController

# fastAPI server activate code
# uvicorn ChatbotController:app --reload
# uvicorn ChatbotController:app --reload --port 8000 --host 0.0.0.0

# or try this
# python -m uvicorn ChatbotController:app --reload

app = FastAPI()

app.include_router(AuthController.router, prefix="/auth", tags=["auth"])

class UserQuery(BaseModel):
    userId : str
    query : str
    isTest : bool

@app.get("/get/chating/{name}")
async def getChat(name : str):
    return ChatingManager.getChatByName(name)

# input user query and get response
@app.post("/chat")
async def inputUserQuery(userQuery : UserQuery):

    userId = userQuery.userId
    query = userQuery.query
    isTest = userQuery.isTest

    # When testing, end function here
    if isTest:
        # Save query to short term memory
        episodeManager.saveQueryInShortTermMemory(userId, query)

        # Get previous dialouge
        memories = episodeManager.getShortTermMemories(userId)

        # Check context and update AI
        isContextChanged = await LLMController.checkContextChange(query)
        if isContextChanged:
            await updateAIChatbot(userId, memories)
            episodeManager.saveQueryInShortTermMemory(userId, query)
        return {"status": "success", "response":"none"}

    # episodeManager.saveQueryInShortTermMemory(userId, query)
    
    ChatingManager.addChating({"sender_name":userId,"receiver_name":"이루매GPT","content":query})

    node_result, idList = episodeManager.retrieveEpisodeID(query)
  
    retrievedEpisodes = episodeManager.retrieveEpisodeByID(userId, idList)
    
    shortTermMemories = episodeManager.getShortTermMemories(userId)
    
    # Generate response and save it to short term memory
    response = await LLMController.generateResponse(query, retrievedEpisodes,shortTermMemories)

    response = response.replace('"', "")

    ChatingManager.addChating({"sender_name":"이루매GPT","receiver_name":userId,"content":response})

    #episodeManager.saveQueryInShortTermMemory(userId, response)

    return {"status": "success", "response": response, "message": "get response from chatbot"}

# finish chat
# @app.post("/finish")
# async def finishTalking(user: UserQuery):
#     await updateAIChatbot(user.userId)
#     return {"status": "success", "message": "finished talking with chatbot"}

# Update episode of the AI Chatbot
async def updateAIChatbot(userId : str, memories : str):
    # 에피소드 메니저 우선 비활성화
    episodeId = episodeManager.createEpisode(userId)
    summarized = await LLMController.summarize(memories)
    await reflectNewKnowledge(userId, summarized, episodeId)
    return

# Reflect new Knowledge
async def reflectNewKnowledge(userId : str, newInfo : str, sourceEpisodeId : int):
    relationTuples = await LLMController.extractRelationship(newInfo)
    knowledgeManager.updateKnowledgeGraph(relationTuples, sourceEpisodeId)
    return
