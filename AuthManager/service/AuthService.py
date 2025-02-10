import pytz
import sys
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import mysql.connector
from datetime import datetime
import random
from passlib.context import CryptContext
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.jwtUtil import create_access_token

kst = pytz.timezone('Asia/Seoul')

current_directory = os.path.dirname(os.path.abspath(__file__))

load_dotenv(dotenv_path=current_directory+"/globals/.env")

user = os.getenv('user')
password = os.getenv('password')
devuser = os.getenv('devuser')
devpassword = os.getenv('devpassword')
host = os.getenv('host')
server_type=os.getenv('servertype')
ISSUER = os.getenv("issuer")

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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def joinProcess(user):
    userId = user.userId
    password = pwd_context.hash(user.password)
    name = user.name
    
    user_info=[userId,password,name]
    sql = "INSERT INTO user (user_id,password,name) VALUES (%s,%s,%s)"

    cursor.execute(sql,user_info)
    connection.commit()

    print("데이터가 성공적으로 삽입되었습니다.")
    print(user_info)

    return {"status":200, "message":"회원가입에 성공하셨습니다."}

def loginProcess(userId, password):
    #DB에서 user 정보 가지고 오기
    sql = "SELECT * FROM user WHERE user_id = %s"
    
    cursor.execute(sql, (userId,))

    # 결과 가져오기
    user = (cursor.fetchall())[0]
    
    print(user)
    
    if not user or not pwd_context.verify(password, user["password"]):
        return {"status":400 , "message":"실패"}
    accessToken = "Bearer "+create_access_token({"userId":user["user_id"],"name":user["name"],"iss":ISSUER})
    
    return {"status":200, "message":"성공","aceessToken":accessToken}