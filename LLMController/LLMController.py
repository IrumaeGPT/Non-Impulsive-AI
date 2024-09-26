from .openaikey import client
from . import prompt

# Return true if context is changed
async def checkContextChange(query : str, memories : str) : 
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


async def chooseTopicToTalk(query : str, memories : str, episodes : list[str]):

    return