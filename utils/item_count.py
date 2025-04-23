import json

# JSON 파일 경로
file_path = "output/conversations_952_single.jsonl"

def count_ids_in_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    # 'id' 키의 개수를 세기
    id_count = sum(1 for item in data if "id" in item)
    return id_count

# 결과 출력
id_count = count_ids_in_json(file_path)
print(f"Total number of 'id': {id_count}")