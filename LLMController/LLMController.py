from .openaikey import client
from openai import OpenAI
from . import prompt
import ast
from . import memories
import json

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
        return True, value
    elif "동일" in result:
        return False, memories
    else:
        return False, memories


# Summarize input memories
async def summarize(memories : str):
    memories = "\n".join(memories)
    response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.5,
    top_p=0.5,
    messages=[
        {"role": "system", "content": prompt.summarizePrompt},
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

async def chooseTopicToTalk(query, memories, episodes):
    client = OpenAI(api_key="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")
    episodeString = ""
    for episode in episodes:
        episodeString += episode
    print(memories)
    userPrompt ="<입력된 문장>\n" + query + "\n\n" \
        + "<갖고 있는 기억>\n" + episodeString
    response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.5,
    top_p=0.5,
    messages=[
        {"role": "system", "content": prompt.topicPrompt},
        {"role": "user", "content": userPrompt},
    ])
    topics = response.choices[0].message.content
    topics = ast.literal_eval(topics)

    return topics

async def generateResponse(query : str, memories : str, topics : list[str], retrievedEpisodes : dict):
    client = OpenAI(api_key="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")
    userPrompt = "\n\n" + "<입력된 문장>\n" + query + "\n\n"
    i = 1
    for topic in topics:
        memory = ""
        for episode in retrievedEpisodes[topic]:
            memory+=episode
        userPrompt += "<답변주제" + str(i) + ">\n" + topic + "\n\n" + \
            "<갖고 있는 관련 기억>\n" + memory + "\n\n"
        i += 1
    response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.5,
    top_p=0.5,
    messages=[
        {"role": "system", "content": prompt.responsePrompt},
        {"role": "user", "content": userPrompt},
    ])
    print(userPrompt)
    return response.choices[0].message.content
