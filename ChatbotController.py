from fastapi import FastAPI
from LLMController import LLMController
# import episodeManager.api.episodeManagerLocal as episodeManager
from episodeManager import episodeManager as episodeManager
from episodeManager import ChatingManager as ChatingManager
from KnowledgeManager import Knowledge as knowledgeManager
from pydantic import BaseModel
from typing import List
from AuthManager.controller import AuthController

# fastAPI server activate code
# uvicorn ChatbotController:app --reload
# uvicorn ChatbotController:app --reload --port 8000 --host 0.0.0.0

# or try this
# python -m uvicorn ChatbotController:app --reload

app = FastAPI()

app.include_router(AuthController.router, prefix="/auth", tags=["auth"])

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

    ChatingManager.addChating({"sender_name":userId,"receiver_name":"이루매GPT","content":query})
    
    knowldgeMemories, episodeMemories = episodeManager.retrieveEpisodes(userId, query)

    # Retrieve episodes about query and choose topics
    topics =  await LLMController.chooseTopicToTalk(query, '\n'.join(knowldgeMemories), '\n'.join(episodeMemories))

    # Retrieve episodes about each topic
    retrievedEpisodes = [None] * len(topics)
    retrievedKnowldgeMemories = [None] * len(topics)
    # 중복된 기억은 모두 제거 하기 위해 이중 반복문
    for i in range(len(topics)):
        retrievedKnowldgeMemories[i], retrievedEpisodes[i] = episodeManager.retrieveEpisodes(userId, topics[i])
        for j in range(i):
            retrievedKnowldgeMemories[i] = [value for value in retrievedKnowldgeMemories[i] if value not in retrievedKnowldgeMemories[j]]
            retrievedEpisodes[i] = [value for value in retrievedEpisodes[i] if value not in retrievedEpisodes[j]]

    #for i in range(len(topics)):
    #    print("Topic : ", topics[i])
    #    print("<추출된 지식그래프 텍스트>\n", retrievedKnowldgeMemories[i], "\n\n")

    # Generate response and save it to short term memory
    response = await LLMController.generateResponse(query, topics, retrievedKnowldgeMemories, retrievedEpisodes)

    response = response.replace('"', "")

    ChatingManager.addChating({"sender_name":"이루매GPT","receiver_name":userId,"content":response})

    #episodeManager.saveQueryInShortTermMemory(userId, response)

    return {"status": "success", "response": response, "message": "get response from chatbot"}

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
    #print(summarized)
    await reflectNewKnowledge(userId, summarized, episodeId)
    return

# Reflect new Knowledge
async def reflectNewKnowledge(userId : str, newInfo : str, sourceEpisodeId : int):
    relationTuples = await LLMController.extractRelationship(newInfo)
    #print(relationTuples)
    knowledgeManager.updateKnowledgeGraph(relationTuples, sourceEpisodeId)
    return


@app.get("/get/chating/{name}")
async def getChat(name : str):
    print(name)
    return ChatingManager.getChatByName(name)
