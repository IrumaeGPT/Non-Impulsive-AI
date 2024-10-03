from neo4j import GraphDatabase

# Neo4j에 연결하기 위한 드라이버 설정
uri = "bolt://localhost:7687"  # 기본적으로 Neo4j는 이 포트를 사용
username = "neo4j"
password = "12345678"

driver = GraphDatabase.driver(uri, auth=(username, password))

# 노드 생성 함수
def create_node(tx, word, embedding):
    query = """
    CREATE (p:Word {name: $word, embedding: $embedding})
    """
    tx.run(query, word=word, embedding=embedding)

# 관계 생성 함수
def create_relationship(tx, fromWord, toWord, relationship, episodeId):
    query = f"""
    MATCH (w1:Word {{name: $fromWord}}), (w2:Word {{name: $toWord}})
    CREATE (w1)-[r:{relationship} {{episodeId: $episodeId}}]->(w2)
    """
    tx.run(query, fromWord=fromWord, toWord=toWord, episodeId=episodeId)

# 노드를 삭제하는 함수
def delete_node(tx, word):
    query = f"""
    MATCH (n:Word {{name: $word}})
    DETACH DELETE n
    """
    tx.run(query, word=word)


# 예시 임베딩 값
철수_embedding = [0.23, 0.11, 0.45, 0.9, 0.01, 0.3]
영희_embedding = [0.21, 0.21, 0.43, 0.94, 0.21, 0.33]

# 세션을 통해 노드와 관계를 생성
with driver.session() as session:
    session.execute_write(create_node, "철수", 철수_embedding)
    session.execute_write(create_node, "영희", 영희_embedding)
    session.execute_write(create_relationship, "철수", "영희", "좋아한다", 123)

# 드라이버 종료
driver.close()