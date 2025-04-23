import json

# JSON 파일 경로
input_file_path = "output/conversations_2k_multi.json"
output_file_path = "output/conversations_2k_multi.jsonl"

def convert_json_to_jsonl(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as input_file:
        data = json.load(input_file)  # JSON 파일 로드

    with open(output_path, "w", encoding="utf-8") as output_file:
        for item in data:
            output_file.write(json.dumps(item, ensure_ascii=False) + "\n")  # JSONL 형식으로 저장

# 변환 실행
convert_json_to_jsonl(input_file_path, output_file_path)
print(f"JSON 파일이 JSONL 파일로 변환되었습니다: {output_file_path}")