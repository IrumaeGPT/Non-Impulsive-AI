from fastapi import FastAPI
from LLMController import LLMController
# import episodeManager.api.episodeManagerLocal as episodeManager
from episodeManager import episodeManager as episodeManager
from KnowledgeManager import Knowledge as knowledgeManager
from pydantic import BaseModel
from typing import List

# fastAPI server activate code
# uvicorn ChatbotController:app --reload
# uvicorn ChatbotController:app --reload --port 8000 --host 0.0.0.0

# or try this
# python -m uvicorn ChatbotController:app --reload

app = FastAPI()

class InitialInfos(BaseModel):
    userId : str
    # infos : List[str] = []

class UserQuery(BaseModel):
    userId : str
    query : str
    isTest : bool

class Information:
    knowledge : str
    sourceEpisode : str

@app.get("/test")
async def test():
    return "hello world"

# initialize user id
@app.post("/initialize")
async def initialize(user: InitialInfos):
    userId = user.userId
    episodeManager.initialUser(userId)
    # for info in user.infos:
    #     reflectNewKnowledge(userId, info, -1)
    # return {"status": "success", "message": "initialized user"}
    return

# input user query and get response
@app.post("/chat")
async def inputUserQuery(userQuery : UserQuery):

    userId = userQuery.userId
    query = userQuery.query
    isTest = userQuery.isTest
    recalledInformations = List[Information]

    # Save query to short term memory
    # 에피소드 메니저 우선 비활성화
    episodeManager.saveQueryInShortTermMemory(userId, query)

    # Get previous dialouge
    # 에피소드 메니저 우선 비활성화
    memories = episodeManager.getShortTermMemories(userId)

    # Check context and update AI
    isContextChanged = await LLMController.checkContextChange(query)
    if isContextChanged:
        await updateAIChatbot(userId, memories)
        # 에피소드 메니저 우선 비활성화
        episodeManager.saveQueryInShortTermMemory(userId, query)

    # When testing, end function here
    if isTest:
        return {"status": "success", "response":"none"}

    knowleage, episodeIdList = knowledgeManager.getMemoryByKnowlegeGraph(query)
    episodeIdList = set(episodeIdList)
    print("<추출된 지식그래프 텍스트>\n", knowleage)
    print("<추출된 episodeIdList>\n", episodeIdList)
    return {"status": "success", "response":"none"}

    # Retrieve episodes about query and choose topics
    #episodes =  episodeManager.retrieveEpisodes(userId, query)
    #retrievedEpisodes[query] = episodes
    #topics =  await LLMController.chooseTopicToTalk(query, memories, episodes)

    # Retrieve episodes about each topic
    #for topic in topics:
    #    episodes =  episodeManager.retrieveEpisodes(userId, topic)
    #    retrievedEpisodes[topic] = episodes

    # Generate response and save it to short term memory
    #response = await LLMController.generateResponse(query, memories, topics, retrievedEpisodes)
    #episodeManager.saveQueryInShortTermMemory(userId, response)

    #return {"status": "success", "response": response, "message": "get response from chatbot"}

# finish chat
@app.post("/finish")
async def finishTalking(user: UserQuery):
    await updateAIChatbot(user.userId)
    return {"status": "success", "message": "finished talking with chatbot"}

# Get every saved episodes
@app.post("/episodes/{userId}")
async def getEpisodes(userId : str):
    # episodes = episodeManager.getEpisodesMemory(userId)
    # return episodes
    return

# Update episode of the AI Chatbot
async def updateAIChatbot(userId : str, memories : str):
    # 에피소드 메니저 우선 비활성화
    episodeId = episodeManager.createEpisode(userId)
    summarized = await LLMController.summarize(memories)
    print(summarized)
    await reflectNewKnowledge(userId, summarized, episodeId)
    return

# Reflect new Knowledge
async def reflectNewKnowledge(userId : str, newInfo : str, sourceEpisodeId : int):
    relationTuples = await LLMController.extractRelationship(newInfo)
    print(relationTuples)
    knowledgeManager.updateKnowledgeGraph(relationTuples, sourceEpisodeId)
    return
