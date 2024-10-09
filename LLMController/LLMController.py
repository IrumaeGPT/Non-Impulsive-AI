from .openaikey import client
from . import prompt

messages = []

# Return true if context is changed
async def checkContextChange(query : str, memories : str) :
    response = client.chat.completions.create(
        model="ft:gpt-4o-mini-2024-07-18:personal::AFbk7D7v",
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
    model="gpt-4o-mini",
    temperature=0.5,
    top_p=0.5,
    messages=[
        {"role": "system", "content": prompt.summarizePrompt},
        {"role": "user", "content": memories},
    ])
    return response.choices[0].message.content


async def chooseTopicToTalk(query : str, memories : str, episodes : list[str]):
    userPrompt = "<이전 대화 내용>\n" + memories + "\n\n" + "<입력된 문장>\n" + query + "\n\n" \
        + "<갖고 있는 기억>\n" + episodes
    response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.5,
    top_p=0.5,
    messages=[
        {"role": "system", "content": prompt.topicPrompt},
        {"role": "user", "content": userPrompt},
    ])
    topics = response.choices[0].message.content
    if topics is not list:
        print("topic generating error: not a list")
    return topics

async def generateResponse(query : str, memories : str, topics : list[str], retrievedEpisodes : dict):
    userPrompt = "<이전 대화 내용>\n" + memories + "\n\n" + "<입력된 문장>\n" + query + "\n\n"
    i = 1
    for topic in topics:
        userPrompt += "<답변주제" + i + ">\n" + topic + "\n\n" + \
            "<갖고 있는 관련 기억\n" + retrievedEpisodes[topic] + "\n\n"
        i += 1
    response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.5,
    top_p=0.5,
    messages=[
        {"role": "system", "content": prompt.responsePrompt},
        {"role": "user", "content": userPrompt},
    ])
    return response.choices[0].message.content
