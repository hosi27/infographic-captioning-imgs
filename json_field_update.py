import os
import json

# 폴더 경로 설정
json_folder = "jsons"  # JSON 파일이 있는 폴더
image_folder = "imgs"  # 이미지 파일이 있는 폴더

# 이미지 파일 목록 생성
image_files = {os.path.splitext(f)[0]: f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))}

# JSON 폴더의 파일 처리
for json_file in os.listdir(json_folder):
    if json_file.endswith(".json"):  # JSON 파일만 처리
        json_path = os.path.join(json_folder, json_file)

        # JSON 파일 읽기
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # JSON 파일 이름에서 숫자 추출
        json_name = os.path.splitext(json_file)[0]

        # 이미지 파일 이름과 매칭
        if json_name in image_files:
            image_file_name = image_files[json_name]
            data["file_name"] = image_file_name  # "file_name" 필드에 이미지 파일명 추가

            # JSON 파일 저장
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Updated {json_file} with image file name {image_file_name}")
        else:
            print(f"No matching image file for {json_file}")

print("작업 완료!")
