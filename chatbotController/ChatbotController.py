from fastapi import FastAPI
import LLMController.LLMController as LLMController
import episodeManager.api.episodeManager as episodeManager

# fastAPI server activate code
# uvicorn apicontroller:app --reload

# or try this
# python -m uvicorn apicontroller:app --reload

app = FastAPI()

# initialize user id
@app.post("/initialize")
async def initialize(userId : str):
    episodeManager.makeCollection(userId)
    return {"status": "success", "message": "initialized user"}

# input user query and get response
@app.post("/chat")
async def inputUserQuery(userId : str, query : str, isTest : bool, checkContext : bool):

    # Get previous dialouge
    retrievedEpisodes = dict()
    memories = await episodeManager.getShortTermMemories(userId)

    # Check context and update AI
    if checkContext:
        isContextChanged = await LLMController.checkContextChange(query, memories)
        if isContextChanged:
            updateAIChatbot(userId)
    
    # Save query to short term memory
    await episodeManager.saveQueryInShortTermMemory(userId, query)

    # When testing, end function here
    if isTest:
        return {"status": "success", "response":"none"}

    # Retrieve episodes about query and choose topics
    episodes = episodeManager.retrieveEpisode(userId, query)
    retrievedEpisodes[query] = episodes
    topics = LLMController.ChooseTopicToTalk(query, memories, episodes)
    
    # Retrieve episodes about each topic
    for topic in topics:
        episodes = episodeManager.retrieveEpisodes(userId, topic)
        retrievedEpisodes[topic] = episodes

    # Generate response and save it to short term memory
    response = LLMController.generateResponse(query, memories, topics, retrievedEpisodes)
    episodeManager.saveQueryInShortTermMemory(userId, response)
    
    return {"status": "success", "response": response, "message": "get response from chatbot"}

# finish chat
@app.post("/finish")
async def finishTalking(userId : str):
    updateAIChatbot(userId)
    return {"status": "success", "message": "finished talking with chatbot"}

# Update episode of the AI Chatbot
async def updateAIChatbot(userId : str):
    memories = episodeManager.getShortTermMemories(userId)
    episode = LLMController.summarize(memories)
    episodeManager.updateEpisodeMemory(userId, episode)
    return