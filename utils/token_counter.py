import tiktoken
import json

# JSON 파일 로드
file_path = "test_data/json/0680.json"  # 네가 저장한 JSON 파일 경로

with open(file_path, "r", encoding="utf-8") as f:
    json_content = f.read()

# 토큰 인코더 설정 (GPT-4o 기준)
encoder = tiktoken.encoding_for_model("gpt-4o")

# 토큰 수 계산
token_count = len(encoder.encode(json_content))

print(f"총 토큰 수: {token_count}")
