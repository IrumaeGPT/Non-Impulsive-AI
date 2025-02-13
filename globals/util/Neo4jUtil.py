import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

current_directory = os.path.dirname(os.path.abspath(__file__))

load_dotenv(dotenv_path=current_directory+"../.env")

devneo4juser = os.getenv('devneo4juser')
devneo4jpassword = os.getenv('devneo4jpassword')
neo4juser = os.getenv('neo4juser')
neo4jpassword = os.getenv('neo4jpassword')

server_type = os.getenv('servertype')

if(server_type=="dev"):
    uri = "bolt://localhost:7687"  
    username = devneo4juser
    password = devneo4jpassword
##Neo4j에 연결하기 위한 드라이버 설정 (local)
else:
    uri = "bolt://localhost:7687"  
    username = neo4juser
    password = neo4jpassword

driver = GraphDatabase.driver(uri, auth=(username, password))