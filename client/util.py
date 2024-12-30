import pandas as pd
import re
from openai import OpenAI
from tqdm import tqdm

client = OpenAI(api_key="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")

eval_prompt = """다음 대화는 두 사람이 이야기하는 것이다.
발화자를 추측해서 A와 B로 구분하여 각 문장마다 앞에 발화자를 표시하여 대화를 다시 적어줘.
"""

data_prompt = """다음 대화는 A와 B가 이야기하는 것이다.
대화에서 추측가능한 정보를 문제로 만들 것인데, 질문과 답변을 각각 생성해줘.
"""

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

def split_and_format_text():
    with open("data/sample.txt", 'r', encoding='utf-8') as file:
        text = file.read()
    # A: 또는 B:로 시작하는 문장을 찾아서 그 앞에 개행을 넣습니다.
    formatted_text = re.sub(r'(A:|B:)', r'\n\1', text)

    # 텍스트의 앞부분에 개행이 들어갈 수 있으므로 strip으로 앞뒤 공백 제거
    formatted_text = formatted_text.strip()
    with open("data/sample2.txt", "w") as file:
        file.write(formatted_text)


def chatgpt_work(s):
    response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=[
                    {"role": "system", "content": eval_prompt},
                    {"role": "user", "content":s}
                ])
    result = response.choices[0].message.content
    return result

def chatgpt_eval(s):
    response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=[
                    {"role": "system", "content": data_prompt},
                    {"role": "user", "content":s}
                ])
    result = response.choices[0].message.content
    return result

def get_data():
    df = pd.read_csv('OPELA/data/oplea_open_data.csv')
    #print(df.head(5))
    #print(df.columns)
    #print(df.info())
    #print(df["total_turn"].value_counts())
    #print(df[df['doc_id'].str.contains("151")])
    print(df[df['persona_name_original'].str.contains("프로관심러")]["total_turn"])
    #print(df.loc[2]['user_text_all'])
    #persona_text_all.txt
    df_pro = df[df['persona_name_original'].str.contains("프로관심러")]["user_text_all"]

    with open("user_text_all.txt", "w") as file:
        for d in df_pro:
            file.write(chatgpt_work(d))
            file.write("\n")

def get_qna():
    df = pd.read_csv('OPELA/data/oplea_open_data.csv')
    #print(df.head(5))
    #print(df.columns)
    #print(df.info())
    #print(df["total_turn"].value_counts())
    #print(df[df['doc_id'].str.contains("151")])
    print(df[df['persona_name_original'].str.contains("프로관심러")]["total_turn"])
    #print(df.loc[2]['user_text_all'])
    #persona_text_all.txt
    df_pro = df[df['persona_name_original'].str.contains("프로관심러")]["user_text_all"]

    with open("new_data/user_text_all.txt", "w") as file1, open("new_data/qna_sample.txt", "w") as file2:
        for d in tqdm(df_pro):
            user_text = chatgpt_work(d)
            file1.write(user_text)
            file1.write("\n")

            file2.write(chatgpt_eval(user_text))
            file2.write("\n\n")

            file1.flush()
            file2.flush()
