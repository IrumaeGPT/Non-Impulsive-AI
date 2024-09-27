from .openaikey import client
from openai import OpenAI
from . import prompt
import ast

# Return true if context is changed
async def checkContextChange(query : str, memories : str) : 
    client = OpenAI(api_key="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")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.5,
        top_p=0.5,
        messages=[
            {"role": "system", "content": prompt.contextCheckPrompt},
            {"role": "user", "content":"<이전 대화 내용>\n" + memories + "\n\n<입력된 문장>" + query + "\n\n<결과>"},
    ])
    result = response.choices[0].message.content
    if "변화" in result:
        return True
    elif "동일" in result:
        return False
    else:
        return False
    

# Summarize input memories
async def summarize(memories : str):
    response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.5,
    top_p=0.5,
    messages=[
        {"role": "system", "content": prompt.summarizePrompt},
        {"role": "user", "content": memories},
    ])
    return response.choices[0].message.content


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