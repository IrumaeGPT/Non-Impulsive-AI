import pytz
from fastapi.responses import JSONResponse
from datetime import datetime
from globals.util import DBUtil as DButil


kst = DButil.kst
connection = DButil.connection
cursor = DButil.cursor

def addChating(data):
    sender_name = data["sender_name"]
    receiver_name = data["receiver_name"]
    content = data["content"]
    day_time = datetime.now(kst)
    
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