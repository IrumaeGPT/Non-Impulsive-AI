import requests, json
import urllib.parse
import ast
import re
from openai import OpenAI
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

current_directory = os.path.dirname(os.path.abspath(__file__))

load_dotenv(dotenv_path=current_directory+"/../episodeManager/.env")

apikey = os.getenv("apikey")

from tqdm import tqdm


# current_directory = os.path.dirname(os.path.abspath(__file__))

# load_dotenv(dotenv_path=current_directory+"../episodeManager/.env")

# server_type=os.getenv('servertype')

client = OpenAI()


eval_prompt = """다음은 대화 내용에서 기억을 잘하고 있는지 판단하는 테스크를 진행한다.
질문과 정답이 주어지면 이를 바탕으로 "답변"이 얼마나 정답과 유사한지 0-100 사이의 점수로 매긴다.
반환값 : {점수}\n
"""

gpt_prompt = """다음 A와 B의 대화를 반영하여 다음의 올 A의 답변을 하나만 "문장으로" 작성해줘
출력 형식 : {생성 문장}\n
"""

# Local
from util import get_data, split_and_format_text

#base_url = "http://sw.uos.ac.kr:8000/"

base_url = "http://localhost:8000/"

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


def insert_first_data(userId):
    userId = userId
    #initialize(userId)
    with open("new_data/user_text_all.txt", 'r', encoding='utf-8') as file:
        count = 0
        for line in tqdm(file):
            count += 1
            #if count < 238:
            #    continue
            line = line.strip()
            chat(userId, line, True, True)


def one_chat(userId):
    text = input("AI 캐릭터에게 할 질문을 입력하세요(종료 - q) :\n")
    while text != "q":
        rps = chat(userId, "B: " + text, False, True)
        print("답변 :\n" + rps["response"] + "\n-------------------------\n")
        text = input("AI 캐릭터에게 할 질문을 입력하세요(종료 - q) :\n")
    # finish(userId)

def eval(userId):
    score = 0
    count = 0
    with open('new_data/questions.txt', 'r',encoding='utf-8') as file1, open('new_data/answers.txt', 'r',encoding='utf-8') as file2:
        print("Evaluation...")
        while True:

            client = OpenAI(api_key=apikey)

            # 각각의 파일에서 한 줄씩 읽기
            test = file1.readline()
            awnser = file2.readline()

            # 두 파일의 끝에 도달하면 반복문을 종료
            if not test and not awnser:
                break

            # AI 캐릭터로부터 답변 반환
            AI_response = chat(userId, "B: " + test, False, True)

            response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=[
                    {"role": "system", "content": eval_prompt},
                    {"role": "user", "content":"질문 : " + test + "\n정답 : " + awnser + "\n답변 : " + AI_response['response']}
                ])

            result = response.choices[0].message.content
            result = re.search(r'\d+', result).group()
            score += int(result)
            count += 1
            print("======= CASE :", count, "=========")
            print("질문 :", test)
            print("정답 :", awnser)
            print("답변 :", AI_response['response'])
            print("점수 :", int(result), "\n")

    print("Eval Complete!\nScore :", score / count)


def eval_chatgpt():
    used_token = 0
    score = 0
    count = 0
    with open("new_data/questions.txt", 'r', encoding='utf-8') as file:
        all_text = file.read()

    with open('data/questions.txt', 'r',encoding='utf-8') as file1, open('data/answers.txt', 'r',encoding='utf-8') as file2:
        print("Evaluation...")
        while True:

            client = OpenAI(api_key=apikey)

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

            token = AI_response.usage.total_tokens
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
            used_token += token
            score += int(result)
            count += 1
            print("======= CASE :", count, "=========")
            print("질문 :", test)
            print("정답 :", awnser)
            print("답변 :", AI_response)
            print("점수 :", result)
            print("사용한 토큰 수 :", token, "\n")

    print("Eval Complete!\nScore :", score / count)
    print("Used Token :", used_token / count)

def eval_chatgpt_rag():
    used_token = 0
    score = 0
    count = 0

    with open('new_data/questions.txt', 'r',encoding='utf-8') as file1, open('new_data/answers.txt', 'r',encoding='utf-8') as file2:
        print("Evaluation...")
        while True:
            client = OpenAI(api_key="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")
            # 각각의 파일에서 한 줄씩 읽기
            test = file1.readline()
            awnser = file2.readline()

            if count <= 6:
                count += 1
                continue

            # 두 파일의 끝에 도달하면 반복문을 종료
            if not test and not awnser:
                break

            # AI 캐릭터로부터 답변 반환
            thread = client.beta.threads.create()
            message = client.beta.threads.messages.create(
  	        		thread_id=thread.id,
  	        		role="user",
  	        		content=test
	            )
            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id="asst_FOXiF24i3WgNWZGZyaYcDBr0"
                )
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            AI_response = messages.data[0].content[0].text.value
            used_token += run.usage.total_tokens
            try:
                AI_response = re.search(r'{(.*?)}', AI_response).group(1)
            except:
                print(AI_response)

            response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=[
                    {"role": "system", "content": eval_prompt},
                    {"role": "user", "content":"질문 : " + test + "\n정답 : " + awnser + "\n답변 : " + AI_response}
                ])

            result = response.choices[0].message.content
            try:
                result = re.search(r'\d+', result).group()
            except:
                print(result)
                result = "0"
            score += int(result)
            count += 1
            print("======= CASE :", count, "=========")
            print("질문 :", test)
            print("정답 :", awnser)
            print("답변 :", AI_response)
            print("점수 :", result)
            print("사용한 토큰 :", run.usage.total_tokens)

    print("Eval Complete!\nScore :", score / count)
    print("Used Token :", used_token / count)
###

if __name__ == "__main__":
    userId = "1208test2"
    #initialize(userId)
    #insert_first_data(userId)
    one_chat(userId)

    # eval(userId)
    #eval_chatgpt()

