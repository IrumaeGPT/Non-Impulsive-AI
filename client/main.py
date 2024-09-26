import requests, json
import urllib.parse
import ast
import sys
import re
from openai import OpenAI

client = OpenAI(api_key="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")

eval_prompt = """다음은 대화 내용에서 기억을 잘하고 있는지 판단하는 테스크를 진행한다.
질문과 정답이 주어지면 이를 바탕으로 "답변"이 얼마나 정답과 유사한지 0-100 사이의 점수로 매긴다.
반환값 : {점수}\n
"""

gpt_prompt = """다음 A와 B의 대화를 반영하여 다음의 올 A의 답변을 하나만 "문장으로" 작성해줘
출력 형식 : {생성 문장}\n
"""

# Local
from util import get_data, split_and_format_text

base_url = "http://127.0.0.1:8800/"

### ChatBotController
def initialize(userId):
    url = base_url + "initialize"

    dic = {
		"userId" : userId,
	}
    r = requests.post(url, json=dic)
    return r.json()

def chat(userId, query, isTest, checkContext):
    url = base_url + "chat"
    dic = {
		"userId" : userId,
        "query" : query,
        "isTest" : isTest,
        "checkContext" : checkContext
	}
    r = requests.post(url, data=json.dumps(dic))
    return r.json()

def finish(userId):
    url = base_url + "finish"
    dic = {
		"userId" : userId,
	}
    r = requests.post(url, data=json.dumps(dic))
    return r.json()
###


def insert_first_data():
    userId = "test002"
    initialize(userId)
    with open("data/sample.txt", 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            chat(userId, line, True, True if line[0] == "B" else False)


def one_chat():
    userId = "test66"
    text = ""
    text = input("AI 캐릭터에게 할 질문을 입력하세요(종료 - q) :\n")
    while text != "q":
        rps = chat(userId, "B: " + text, False, True)
        print("답변 :\n" + rps["response"] + "\n-------------------------\n")
        text = input("AI 캐릭터에게 할 질문을 입력하세요(종료 - q) :\n")
    finish(userId)

def eval():
    score = 0
    count = 0
    userId = "test123"
    with open('data/test.txt', 'r') as file1, open('data/awnser.txt', 'r') as file2:
        print("Evaluation...")
        while True:
            # 각각의 파일에서 한 줄씩 읽기
            test = file1.readline()
            awnser = file2.readline()

            # 두 파일의 끝에 도달하면 반복문을 종료
            if not test and not awnser:
                break

            # AI 캐릭터로부터 답변 반환
            AI_response = chat(userId, "B: " + test, False, True)
            finish(userId)

            response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=[
                    {"role": "system", "content": eval_prompt},
                    {"role": "user", "content":"질문 : " + test + "\n정답 : " + awnser + "\n답변 : " + AI_response}
                ])

            result = response.choices[0].message.content
            result = re.search(r'\d+', result).group()
            score += int(result)
            count += 1
            print("======= CASE :", count, "=========")
            print("질문 :", test)
            print("정답 :", awnser)
            print("답변 :", AI_response)
            print("점수 :", score, "\n")

    print("Eval Complete!\nScore :", score / count)


def eval_chatgpt():
    score = 0
    count = 0
    with open("data/sample.txt", 'r', encoding='utf-8') as file:
        all_text = file.read()

    with open('data/test.txt', 'r') as file1, open('data/awnser.txt', 'r') as file2:
        print("Evaluation...")
        while True:
            # 각각의 파일에서 한 줄씩 읽기
            test = file1.readline()
            awnser = file2.readline()

            # 두 파일의 끝에 도달하면 반복문을 종료
            if not test and not awnser:
                break

            # AI 캐릭터로부터 답변 반환
            AI_response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=[
                    {"role": "system", "content": gpt_prompt},
                    {"role": "user", "content": all_text + "\n" + "B: " + test}
                ])

            AI_response = AI_response.choices[0].message.content
            AI_response = re.search(r'{(.*?)}', AI_response).group(1)

            response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=[
                    {"role": "system", "content": eval_prompt},
                    {"role": "user", "content":"질문 : " + test + "\n정답 : " + awnser + "\n답변 : " + AI_response}
                ])

            result = response.choices[0].message.content
            result = re.search(r'\d+', result).group()
            score += int(result)
            count += 1
            print("======= CASE :", count, "=========")
            print("질문 :", test)
            print("정답 :", awnser)
            print("답변 :", AI_response)
            print("점수 :", result, "\n")

    print("Eval Complete!\nScore :", score / count)
###

if __name__ == "__main__":
    #insert_first_data()
    one_chat()
