from globals.util import DBUtil as DBUtil
from KnowledgeManager.Knowledge import getMemoryByKnowlegeGraph

connection = DBUtil.connection
cursor = DBUtil.cursor

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
    node_result , episodeIds = getMemoryByKnowlegeGraph(query)

    return node_result, episodeIds

