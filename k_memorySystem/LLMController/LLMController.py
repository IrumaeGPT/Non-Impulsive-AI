from .openaikey import client
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

    if "변화" in result:
        memories = list()
        memories.append(query)
        return True
    elif "동일" in result:
        return False
    else:
        return False


# Summarize input memories
async def summarize(memories : str):
    memories = "주어진 대화 내용:\n" + "\n".join(memories)
    response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.8,
    top_p=0.8,
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

async def chooseTopicToTalk(query, knowldgeMemories, episodeMemories):
   
    userPrompt ="<입력된 문장>\n" + query



    userPrompt ="<지식>\n" + knowldgeMemories + "\n\n" \
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

    with open("used_token.txt", "a") as file:
        file.write("[" + str(response.usage.total_tokens)+ ",")

    return topics

async def generateResponse(query : str, retrievedEpisodes : list[str],shortTemrMemories : str):

    userPrompt = "<입력된 문장>\n" + query + "\n\n"
    userPrompt += "<관련 대화 내용>\n" + '\n'.join(retrievedEpisodes) + '\n\n'
    userPrompt += shortTemrMemories
  
    response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.5,
    top_p=0.5,
    messages=[
        {"role": "system", "content": prompt.responsePrompt},
        {"role": "user", "content": userPrompt},
    ])

    with open("used_token.txt", "a") as file:
        file.write(str(response.usage.total_tokens) + ",")
    return response.choices[0].message.content
