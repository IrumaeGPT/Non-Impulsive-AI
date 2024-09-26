from fastapi import FastAPI
from LLMController import LLMController
import episodeManager.api.episodeManagerLocal as episodeManager
from pydantic import BaseModel
# fastAPI server activate code
# uvicorn ChatbotController:app --reload

# or try this
# python -m uvicorn ChatbotController:app --reload

app = FastAPI()

class Item(BaseModel):
    userId : str
    query : str
    isTest : bool
    checkContext : bool

class User(BaseModel):
    userId : str

# initialize user id
@app.post("/initialize")
async def initialize(user: User):
    userId = user.userId
    episodeManager.make_collection(userId)
    return {"status": "success", "message": "initialized user"}

# input user query and get response
@app.post("/chat")
async def inputUserQuery(item : Item):

    userId = item.userId
    query = item.query
    isTest = item.isTest
    checkContext = item.checkContext
    
    # Get previous dialouge
    retrievedEpisodes = dict()
    memories = episodeManager.getShortTermMemories(userId)

    # Check context and update AI
    if checkContext and memories:
        isContextChanged = await LLMController.checkContextChange(query, memories)
        if isContextChanged:
            # print("memories: \n" + memories + "\nquery: " + query +"\n\n")
            await updateAIChatbot(userId, memories)
    
    # Save query to short term memory
    episodeManager.saveQueryInShortTermMemory(userId, query)

    # When testing, end function here
    if isTest:
        return {"status": "success", "response":"none"}

    # Retrieve episodes about query and choose topics
    episodes =  episodeManager.retrieveEpisodes(userId, query)
    retrievedEpisodes[query] = episodes
    topics =  await LLMController.chooseTopicToTalk(query, memories, episodes)
    
    # Retrieve episodes about each topic
    for topic in topics:
        episodes =  episodeManager.retrieveEpisodes(userId, topic)
        retrievedEpisodes[topic] = episodes

    # Generate response and save it to short term memory
    response = await LLMController.generateResponse(query, memories, topics, retrievedEpisodes)
    episodeManager.saveQueryInShortTermMemory(userId, response)
    
    return {"status": "success", "response": response, "message": "get response from chatbot"}

# finish chat
@app.post("/finish")
async def finishTalking(user: User):
    await updateAIChatbot(user.userId)
    return {"status": "success", "message": "finished talking with chatbot"}


@app.post("/episodes/{userId}")
async def getEpisodes(userId : str):
    episodes = episodeManager.getEpisodesMemory(userId)
    return episodes

# Update episode of the AI Chatbot
async def updateAIChatbot(userId : str, memories : str):
    episode = await LLMController.summarize(memories)
    # print("episode: " + episode)
    episodeManager.updateEpisodeMemory(userId, episode)
    return