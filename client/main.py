import pandas as pd
import re

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

def get_data():
    df = pd.read_csv('OPELA/data/oplea_open_data.csv')
    print(df.head(5))
    print(df.columns)
    print(df.info())
    print(df["total_turn"].value_counts())
    print(df[df['doc_id'].str.contains("151")])
    print(df[df['persona_name_original'].str.contains("프로관심러")]["total_turn"])
    #print(df.loc[2]['user_text_all'])
    #persona_text_all.txt

    with open("persona_text_all.txt", "w") as file:
        file.write(df.loc[2]['persona_text_all'])


if __name__ == "__main__":
    get_data()
