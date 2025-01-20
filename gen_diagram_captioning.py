import os
import json
import openai
import re

# GPT API 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# JSON 파일이 저장된 폴더 경로
DATA_FOLDER = "./test_json"

# JSONL 저장 경로
OUTPUT_FILE = "conversation_dataset.jsonl"

# GPT API를 사용하여 대화셋 생성
def generate_conversation(json_data, filename):
    prompt = f"""
    아래 JSON 데이터를 기반으로 한 턴의 대화 데이터를 생성해 주세요.
    JSON 데이터를 모두 활용하여 이미지에 대한 설명을 자세히 포함해야 합니다.
    
    JSON 데이터:
    {json.dumps(json_data, ensure_ascii=False, indent=4)}

    형식 예시:
    {{
      "id": "{filename.replace('.json', '')}",
      "image": "{json_data.get('file_name', filename.replace('.json', '.png'))}",
      "conversations": [
        {{
          "from": "human",
          "value": "<image>\\n이 이미지는 무엇을 설명하고 있나요?"
        }},
        {{
          "from": "gpt",
          "value": "해당 이미지에 대한 설명을 여기에 추가하세요."
        }}
      ]
    }}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "너는 JSON으로 추출된 이미지 정보를 기반으로 질의응답을 만드는 AI 어시스턴트야."},
                  {"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# JSON 파일 읽기 및 대화 데이터 생성
def process_json_files():
    with open(OUTPUT_FILE, "a", encoding="utf-8") as jsonl_file:
        for filename in os.listdir(DATA_FOLDER):
            if filename.endswith(".json"):
                file_path = os.path.join(DATA_FOLDER, filename)
                try:
                    with open(file_path, "r", encoding="utf-8-sig") as f:
                        # data = json.load(f)  # JSON 파일 로드
                        data=f.read().strip()
                    json_data = json.loads(data)
                    # GPT API 호출하여 대화셋 생성
                    conversation_json = generate_conversation(json_data, filename)
                    # print(conversation_json)
                    cleaned_json = conversation_json.replace("```", "").replace("json", "") # 리턴된 문자열에서 json 규격을 벗어난 문자들을 제거
                    # print(cleaned_json)
                    # print(f"GPT response for {filename}: {conversation_json}")

                    # JSON 형식 검증 및 파싱
                    if not cleaned_json.strip():
                        print(f"Error: GPT response for {filename} is empty.")
                        continue

                    try:
                        conversation_data = json.loads(cleaned_json)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON from GPT response for {filename}: {e}")
                        continue

                    # JSONL 파일에 추가
                    jsonl_file.write(json.dumps(conversation_data, ensure_ascii=False) + "\n")

                    print(f"Processed: {filename}")
                except json.JSONDecodeError as e:
                    print(f"Error reading {filename}: {e}")
                except UnicodeDecodeError as e:
                    print(f"Error decoding {filename}: {e}")

process_json_files()
