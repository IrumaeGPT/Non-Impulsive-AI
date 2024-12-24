from .openaikey import client
from openai import OpenAI
from . import prompt
import ast
from . import memories
import json
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

current_directory = os.path.dirname(os.path.abspath(__file__))

load_dotenv(dotenv_path=current_directory+"/../episodeManager/.env")

apikey = os.getenv("apikey")

# Return true if context is changed
async def checkContextChange(query : str) :
    global memories
    memories.append(query)
    messages = []
    messages.append({"role": "system", "content": prompt.contextCheckPrompt})
    for s in memories:
        messages.append({"role": "user", "content": s})
        #messages.append({"role": "assistant", "content": "동일"})

    #messages.pop()

    response = client.chat.completions.create(
        model="ft:gpt-4o-mini-2024-07-18:personal::AGLY8ZHM",
        temperature=0.8,
        top_p=0.8,
        messages=messages
    )
    result = response.choices[0].message.content
    print(result)
    if "변화" in result:
        value = memories.copy()
        memories = list()
        memories.append(query)
        return True
    elif "동일" in result:
        return False
    else:
        return False


# Summarize input memories
async def summarize(memories : str):
    memories = "\n".join(memories)
    response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.8,
    top_p=0.8,
    messages=[
        {"role": "system", "content": prompt.summarizePrompt},
        {"role": "user", "content": prompt.summarizeSample},
        {"role": "assistant", "content": prompt.summarizeAwnser},
        {"role": "user", "content": prompt.summarizeSample2},
        {"role": "assistant", "content": prompt.summarizeAwnser2},
        {"role": "user", "content": memories},
    ])
    return response.choices[0].message.content


# extra relationship
async def extractRelationship(summarized_text : str):
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
  			thread_id=thread.id,
  			role="user",
  			content=summarized_text
	    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id="asst_7Ruu1YqvZhYyTWrIfRrgFUqY",
        response_format = {"type":"json_object"}
        )
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
          thread_id=thread.id
        )
        response = messages.data[0].content[0].text.value
        json_response = json.loads(response)
        return json_response["triples"]
    else:
        raise ValueError("관계 추출 부분에서 에러 발생", run.status)

async def chooseTopicToTalk(query, knowldgeMemories, episodeMemories):
    client = OpenAI(api_key=apikey)

    userPrompt ="<지식>\n" + knowldgeMemories + "\n\n" \
        + "<관련 대화 내용>\n" + episodeMemories \
        + "<입력된 문장>\n" + query
    response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.8,
    top_p=0.8,
    messages=[
        {"role": "system", "content": prompt.topicPrompt},
        {"role": "user", "content": userPrompt},
    ])
    topics = response.choices[0].message.content
    topics = ast.literal_eval(topics)

    return topics

async def generateResponse(query : str, topics : list[str], retrievedKnowldgeMemories : list[str], retrievedEpisodes : list[str]):

    client = OpenAI(api_key=apikey)

    userPrompt = "<입력된 문장>\n" + query + "\n\n"
    for i in range(len(topics)):
        userPrompt += "<답변주제" + str(i) + ">\n" + topics[i] + "\n\n" + \
            "<지식>\n" + '\n'.join(retrievedKnowldgeMemories[i]) + "\n\n" \
            + "<관련 대화 내용>\n" + '\n'.join(retrievedEpisodes[i]) + '\n\n'
    response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.5,
    top_p=0.5,
    messages=[
        {"role": "system", "content": prompt.responsePrompt},
        {"role": "user", "content": userPrompt},
    ])
    return response.choices[0].message.content
