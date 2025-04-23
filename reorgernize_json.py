import os
import json

# JSON 파일이 모여있는 폴더 경로
folder_path = "test_data/json_filtered"

# 폴더 내 모든 JSON 파일 처리
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):  # JSON 파일만 처리
        file_path = os.path.join(folder_path, filename)

        # JSON 파일 읽기
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"JSON 파일 읽기 오류: {filename}, 오류: {e}")
                continue

        # "root" 필드 제거 및 내용만 유지
        if "root" in data:
            data = data["root"]
        
            # 변경된 JSON 데이터 저장
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f'"root" 필드 제거 완료: {filename}')
