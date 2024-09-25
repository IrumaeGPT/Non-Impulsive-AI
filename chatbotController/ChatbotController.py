from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import LLMController

# fastAPI server activate code
# uvicorn apicontroller:app --reload

# or try this
# python -m uvicorn apicontroller:app --reload

app = FastAPI()

class InitialInformations(BaseModel):
    intialInformations: List[str]

class Information:
    def __init__(self, knowledge, episode):
        self.knowledge = knowledge
        self.episode = episode

# Set initial inforations about chatbot
@app.post("/intialize")
async def set_initial_information(initializingInformations : InitialInformations):
    # Reflect every initial informations
    for info in initializingInformations.intialInformations:
        await reflect_new_knowledge(info, -1)

    return {"status": "success", "message": "Initial informations processed successfully"}

# input user query and get response
@app.post("/chat")
async def input_user_query(query : str):

    return

# Reflect new incoming knowledge
async def reflect_new_knowledge(newInfo : str, sourceEpisodeId : int):
    relationTuples = LLMController.extract_reationship(newInfo)
    # update_knowledge_graph(relationTuples, sourceEpisodeId)
    return

# Recall knoweldge, episode and return information object list
def recall_knowledge_and_episode(subject : str):
    informations = list()
    # knowledges = recall_knowledge(subject)
    # for key in knowledges.keys():
    #     episode = retrieve_episode(key)
    #     information = Information(knowledges[key], episode)
    #     informations.append(information)
    
    return informations