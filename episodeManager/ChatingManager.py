import pytz
import sys
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import mysql.connector
from datetime import datetime
import random

kst = pytz.timezone('Asia/Seoul')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    

cursor = connection.cursor(dictionary=True)

create_table_query = """
CREATE TABLE IF NOT EXISTS chating (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_name VARCHAR(50) NOT NULL,
    receiver_name VARCHAR(50) NOT NULL,
    content VARCHAR(1000) NOT NULL,
    day_time DATETIME
);
"""

cursor.execute(create_table_query)

def addChating(data):
    sender_name = data["sender_name"]
    receiver_name = data["receiver_name"]
    content = data["content"]
    day_time = datetime.now(kst)
    
    # random_content = str(random.randint(0,101010))
    # random_content = "안녕 나는 이루매 GPT야 잘 부탁해 오늘 밥은 맛있게 먹었니 친구야?"
    chating_info = [sender_name,receiver_name,content,day_time]
    
    sql = "INSERT INTO chating (sender_name, receiver_name, content, day_time) VALUES (%s,%s,%s,%s)"
    
    cursor.execute(sql, chating_info)

    # 변경 사항을 커밋
    connection.commit()

    print("데이터가 성공적으로 삽입되었습니다.")
    print(chating_info)
    
    return {"status":200,"chating_info":chating_info}

def getChatByName(name):
    sql = "SELECT * FROM chating WHERE sender_name = %s OR receiver_name = %s"
    
    cursor.execute(sql,(name,name))

    # 결과 가져오기
    chatings = cursor.fetchall()  # 모든 행 가져오기
    
    for chatting in chatings:
        for key, value in chatting.items():
            if isinstance(value, datetime):
                chatting[key] = value.isoformat()  # datetime을 문자열로 변환
            
    return JSONResponse(content=chatings)