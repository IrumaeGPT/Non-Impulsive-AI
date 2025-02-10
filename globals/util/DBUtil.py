import pytz
import sys
import os
from dotenv import load_dotenv
import mysql.connector

kst = pytz.timezone('Asia/Seoul')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

current_directory = os.path.dirname(os.path.abspath(__file__))

load_dotenv(dotenv_path=current_directory+"../.env")

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
   

def make_init_table(cursor):
    create_table_user = """
    CREATE TABLE IF NOT EXISTS user (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id VARCHAR(50) NOT NULL,
        password VARCHAR(500) NOT NULL,
        name VARCHAR(50) NOT NULL
    );
    """

    create_table_longterm="""
    CREATE TABLE IF NOT EXISTS longterm (
        id INT AUTO_INCREMENT PRIMARY KEY,
        observation VARCHAR(500) NOT NULL,
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

    create_table_chating = """
    CREATE TABLE IF NOT EXISTS chating (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sender_name VARCHAR(50) NOT NULL,
        receiver_name VARCHAR(50) NOT NULL,
        content VARCHAR(1000) NOT NULL,
        day_time DATETIME
    );
    """
        
    cursor.execute(create_table_user)
    cursor.execute(create_table_longterm)
    cursor.execute(create_table_shorterm)
    cursor.execute(create_table_chating)

cursor = connection.cursor(dictionary=True)
make_init_table(cursor)