import mysql.connector
import os
import sys
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from KnowledgeManager.Knowledge import getMemoryByKnowlegeGraph

current_directory = os.path.dirname(os.path.abspath(__file__))

load_dotenv(dotenv_path=current_directory+"/.env")

user = os.getenv('user')
password = os.getenv('password')
devuser = os.getenv('devuser')
devpassword = os.getenv('devpassword')
host = os.getenv('host')
server_type=os.getenv('servertype')

if(server_type=="dev"):
    connection = mysql.connector.connect(
    host=host,       # MySQL 서버 호스트 주소 (로컬이면 'localhost')
    user=devuser,   # MySQL 사용자 이름
    password=devpassword, # MySQL 비밀번호
    database="aicharacter",  # 사용할 데이터베이스 이름
    port=3306 #포트번호
)
else:
# MySQL local 서버에 연결
    connection = mysql.connector.connect(
        host="localhost",       # MySQL 서버 호스트 주소 (로컬이면 'localhost')
        user=user,   # MySQL 사용자 이름
        password=password, # MySQL 비밀번호
        database="aicharacter",  # 사용할 데이터베이스 이름
        port=4000 #포트번호
    )

if connection.is_connected():
    print("MySQL에 성공적으로 연결되었습니다.")

cursor = connection.cursor(dictionary=True) #데이터를 가져올 때 dict 형태로 가지고 오기

create_table_user = """
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
     PRIMARY KEY (id, name)
);
"""

create_table_longterm="""
CREATE TABLE IF NOT EXISTS longterm (
    id INT AUTO_INCREMENT PRIMARY KEY,
    observation VARCHAR(200) NOT NULL,
    episodeid INT NOT NULL,
    user_id INT,
    CONSTRAINT fk_user_longterm FOREIGN KEY (user_id) REFERENCES user(id)
);

"""

create_table_shorterm="""
CREATE TABLE IF NOT EXISTS shorterm (
    id INT AUTO_INCREMENT PRIMARY KEY,
    observation VARCHAR(200) NOT NULL,
    user_id INT,
    CONSTRAINT fk_user_shorterm FOREIGN KEY (user_id) REFERENCES user(id)
);
"""

cursor.execute(create_table_user)
cursor.execute(create_table_longterm)
cursor.execute(create_table_shorterm)

def initialUser(userName):
    user_info=[userName]
    sql = "INSERT INTO user (name) VALUES (%s)"

    cursor.execute(sql,user_info)
    connection.commit()

    print("데이터가 성공적으로 삽입되었습니다.")
    print(user_info)

    return

def saveQueryInShortTermMemory(userName, query):

    userId=find_userId(userName=userName)
    result=[]

    if(userId!=-1):

        shorterm_info=[query,userId]

        sql = "INSERT INTO shorterm (observation,user_id) VALUES (%s,%s)"

        cursor.execute(sql,shorterm_info)
        connection.commit()

        print("데이터가 성공적으로 삽입되었습니다.")
        print(shorterm_info)
    return

def getShortTermMemories(userName):

    userId=find_userId(userName=userName)
    result=[]
    result_str=""

    if(userId!=-1):

        sql = f"SELECT * FROM shorterm WHERE user_id = '{userId}'"

        cursor.execute(sql)  # 쿼리 실행
        result = cursor.fetchall()  # 모든 결과 가져오기

        for item in result:
            result_str+=item["observation"]
            result_str+="\n"
        print(result_str)

    return result_str

def createEpisode(userName):

    userId=find_userId(userName)
    if(userId != -1):
        sql = f"SELECT * FROM longterm WHERE user_id = '{userId}'"
        cursor.execute(sql)
        longterm_memory = cursor.fetchall()
        if(len(longterm_memory)==0):
            episodeId=0
        else:
            episodeId = max(memory['episodeid'] for memory in longterm_memory)+1

        sql = f"SELECT * FROM shorterm WHERE user_id = '{userId}'"
        cursor.execute(sql)
        shorterm_memory = cursor.fetchall()

        for memory in shorterm_memory:
            sql = "INSERT INTO longterm (observation, user_id, episodeid) VALUES (%s, %s, %s)"
            cursor.execute(sql, (memory['observation'], memory['user_id'],episodeId))

        sql = f"DELETE FROM shorterm WHERE user_id = '{userId}'"
        cursor.execute(sql)

        connection.commit()
        return episodeId

    return -1

def find_userId(userName):
    sql = f"SELECT * FROM user WHERE name = '{userName}'"

    cursor.execute(sql)  # 쿼리 실행
    result = cursor.fetchall()  # 모든 결과 가져오기

    if(len(result)==0):
        return -1

    userId=result[0]["id"]
    return userId

def retrieveEpisodes(userName,query):
    episodeMemories=[]
    knowldgeMemories, episodeIds = getMemoryByKnowlegeGraph(query)
    episodeIds = set(episodeIds)
    userId=find_userId(userName)

    for value in episodeIds:
        sql = f"SELECT * FROM longterm WHERE user_id='{userId}' and episodeId='{value}'"
        cursor.execute(sql)  # 쿼리 실행
        result = cursor.fetchall()  # 모든 결과 가져오기
        for item in result:
            episodeMemories.append(item["observation"])

    return knowldgeMemories, episodeMemories


###
def retrieveEpisodeByID(userName,episodeIds):
    episodeMemories=[]
    userId=find_userId(userName)

    for value in episodeIds:
        sql = f"SELECT * FROM longterm WHERE user_id='{userId}' and episodeId='{value}'"
        cursor.execute(sql)  # 쿼리 실행
        result = cursor.fetchall()  # 모든 결과 가져오기
        for item in result:
            episodeMemories.append(item["observation"])

    return episodeMemories

def retrieveEpisodeID(query):
    knowldgeMemories, episodeIds = getMemoryByKnowlegeGraph(query)

    return episodeIds
###

#retrieveEpisodes("냠냠","맥주 먹고싶다..")
# saveQueryInShortTermMemory("다크시니","나 공놀이함")
# saveQueryInShortTermMemory("다크시니","나 활어 먹고 싶네")
# saveQueryInShortTermMemory("다크시니","나는야 까만 고양이")
# getShortTermMemories("다크시니")

# createEpisode("다크시니")
