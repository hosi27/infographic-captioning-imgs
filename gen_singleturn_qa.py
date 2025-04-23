import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import re

# GPT API 설정

# JSON 파일이 저장된 폴더 경로
DATA_FOLDER = "test_data/crowd_labeled/kt_952/json_test"

# JSONL 저장 경로
OUTPUT_FOLDER = "output"  # 결과를 저장할 폴더
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "conversations_952_single_gpt41.jsonl")  # 결과 파일 경로
ERROR_LOG_FILE = os.path.join(OUTPUT_FOLDER, "error_log.txt")  # 에러 로그 경로

# GPT API를 사용하여 대화셋 생성
def generate_conversation(json_data, filename):
    prompt = f"""
    아래 JSON 데이터를 기반으로 한 턴의 대화 데이터를 생성해 주세요. 
    JSON 데이터를 모두 활용하여 이미지에 대한 설명을 자세히 기술해야 합니다.
    
    JSON 데이터:
    {json.dumps(json_data, ensure_ascii=False, indent=4)}

    형식 예시:
    {{
      "id": "{filename.replace('.json', '')}",
      "image": "{json_data.get('file_name', filename.replace('.json', '.png'))}",
      "conversations": [
        {{
          "from": "human",
          "value": "<image>\\n이 다이어그램에서 주요 노드들의 계층 구조와 각 노드의 역할을 설명해 주세요."
        }} 
        {{
          "from": "gpt",
          "value": "해당 이미지에 대한 설명을 여기에 추가하세요."
        }}
      ]
    }}
    """
    response = client.chat.completions.create(model="gpt-4.1",
    messages=[{"role": "system", "content": "너는 JSON으로 추출된 이미지 정보를 기반으로 질의응답을 만드는 AI 어시스턴트야."},
              {"role": "user", "content": prompt}])
    return response.choices[0].message.content

# JSON 파일 읽기 및 대화 데이터 생성
def process_json_files():
    # 에러 로그 파일 초기화
    with open(ERROR_LOG_FILE, "w", encoding="utf-8") as error_log:
        error_log.write("Error Log:\n")    
     
     # JSON 파일이 없으면 생성하고 배열 시작 추가
    # if not os.path.exists(OUTPUT_FILE):
    #     with open(OUTPUT_FILE, "w", encoding="utf-8") as json_file:
    #         json_file.write("[\n")  # JSON 배열 시작

    # 파일별 대화 데이터 생성
    # first_entry = True  # 첫 번째 항목인지 확인
    # with open(OUTPUT_FILE, "a", encoding="utf-8") as json_file:
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".json"):
            file_path = os.path.join(DATA_FOLDER, filename)
            try:
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    data = f.read().strip()
                json_data = json.loads(data)

                # GPT API 호출하여 대화셋 생성
                conversation_json = generate_conversation(json_data, filename)
                cleaned_json = conversation_json.replace("```", "").replace("json", "")  # 불필요한 문자 제거
                # print(cleaned_json)

                # JSON 형식 검증 및 파싱
                if not conversation_json.strip():
                    print(f"Error: GPT response for {filename} is empty.")
                    continue

                # JSON 형식 검증 및 파싱
                try:
                    conversation_data = json.loads(cleaned_json)
                except json.JSONDecodeError as e:
                    error_message = f"Error decoding JSON from GPT response for {filename}: {e}"
                    print(error_message)
                    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as error_log:
                        error_log.write(error_message + "\n")
                    continue

                # JSON 파일에 추가
                # if not first_entry:
                #     json_file.write(",\n")  # 이전 항목 뒤에 쉼표 추가
                # json.dump(conversation_data, json_file, ensure_ascii=False)
                # first_entry = False  # 첫 번째 항목 이후로 설정
                # jsonl 형식으로 저장
                with open(OUTPUT_FILE, "a", encoding="utf-8") as jsonl_file:
                    jsonl_file.write(json.dumps(conversation_data, ensure_ascii=False) + "\n")

                print(f"Processed: {filename}")
            except json.JSONDecodeError as e:
                error_message = f"Error decoding JSON from GPT response for {filename}: {e}"
                print(error_message)
                with open(ERROR_LOG_FILE, "a", encoding="utf-8") as error_log:
                    error_log.write(error_message + "\n")
                continue
            except UnicodeDecodeError as e:
                error_message = f"Error decoding {filename}: {e}"
                print(error_message)
                with open(ERROR_LOG_FILE, "a", encoding="utf-8") as error_log:
                    error_log.write(error_message + "\n")
                continue

    # JSON 배열 닫기
    # with open(OUTPUT_FILE, "a", encoding="utf-8") as json_file:
    #     json_file.write("\n]\n")

    print(f"All data saved to {OUTPUT_FILE}")

process_json_files()