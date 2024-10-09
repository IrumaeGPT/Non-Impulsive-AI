import json
import os
import glob

# 파일 이름 패턴과 범위 설정
file_prefix = "K2-"
folder_path = "data/original_data"
start_num = 1
end_num = 10

contextCheckPrompt = "너는 대화의 맥락이 변화 되었는지 감지해야해. \
이전에 이야기하던 주제와 무관한 새로운 주제가 등장하거나 연관성이 있더라도 주제가 다른 방향으로 전개될 때 맥락이 변경되었다고 볼 수 있어. \
'이전 대화 내용'을 분석해서 '입력된 문장'이 대화 맥락에서 벗어나는 문장인지 '변화' 혹은 '동일'로 결과를 판단해줘."

# JSON 파일을 불러오는 함수
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# 대화를 멀티턴 형식으로 변환하는 함수
def extract_dialog_as_messages(data):
    system_message = {"role": "system", "content": contextCheckPrompt}

    # 결과를 저장할 리스트
    all_conversations = []

    # sessionInfo에서 대화 내용을 추출
    for session in data.get("sessionInfo", []):
        messages = [system_message]  # 첫 번째 시스템 메시지 추가
        dialog_list = session.get("dialog", [])

        i = 0
        for dialog in dialog_list:
            speaker = dialog.get("speaker")
            utterance = dialog.get("utterance")
            context_change = dialog.get("terminate")
            # 메시지 추가
            messages.append({"role": "user", "content": utterance})
            if i != 0:
                if context_change == "true":
                    messages.append({"role": "assistant", "content": "변화"})
                    all_conversations.append({"messages": messages})
                    messages = [system_message]  # 첫 번째 시스템 메시지 추가
                    messages.append({"role": "user", "content": utterance})
                messages.append({"role": "assistant", "content": "동일"})
            i += 1


        # 하나의 대화를 완료했으면 저장
        all_conversations.append({"messages": messages})

    return all_conversations

# 변환된 대화를 파일로 저장하는 함수
def save_conversations_to_json(conversations, output_file):
    with open(output_file, 'a', encoding='utf-8') as file:
        for conversation in conversations:
            json.dump(conversation, file, ensure_ascii=False)
            file.write('\n')  # 각 대화를 구분하는 빈 줄 추가

# JSON 파일 경로 설정
output_file = 'data/processd_data/output.json'  # 출력 파일 경로

# 파일 반복 처리
for num in range(start_num, end_num + 1):
    # 숫자를 5자리로 포맷 (예: 00001, 00002, ...)
    file_num_str = f"{num:05d}"

    # 파일 검색 패턴 (K2-00001-*처럼 뒷부분은 어떤 문자든 가능)
    search_pattern = os.path.join(folder_path, f"{file_prefix}{file_num_str}-*")

    # 해당 패턴에 맞는 파일 목록 가져오기
    files = glob.glob(search_pattern)

    for input_file_name in files:
        json_data = load_json(input_file_name)

    # 대화를 멀티턴 대화 형식으로 변환
    conversations = extract_dialog_as_messages(json_data)

    # 변환된 대화를 JSON 파일로 저장
    save_conversations_to_json(conversations, output_file)
    print(f"대화가 {output_file} 파일에 저장되었습니다.")
