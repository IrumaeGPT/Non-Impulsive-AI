import json

# JSON 파일을 불러오는 함수
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# JSON 데이터의 구조를 출력하는 함수
def print_json_structure(data, indent=0):
    if isinstance(data, dict):
        for key, value in data.items():
            print(' ' * indent + f"{key}: {type(value).__name__}")
            print_json_structure(value, indent + 4)
    elif isinstance(data, list):
        print(' ' * indent + f"List of {len(data)} items")
        if len(data) > 0:
            print_json_structure(data[0], indent + 4)  # 리스트의 첫 번째 아이템 구조 출력
    else:
        print(' ' * indent + f"{type(data).__name__}")

# 파일 경로에 맞는 JSON 파일 불러오기
file_path = 'data/K2-00001-CL33762-CP33206-05-08-S2.json'  # JSON 파일 경로
json_data = load_json(file_path)

# JSON 구조 출력
print_json_structure(json_data)
