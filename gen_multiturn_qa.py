import os
import json
import base64
import time
from openai import OpenAI
import tiktoken

# OpenAI API 키 설정
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 데이터셋 폴더 설정
IMAGE_FOLDER = "test_data/2k/image"  # 이미지 파일이 저장된 폴더
JSON_FOLDER = "test_data/2k/json_test"  # JSON 파일이 저장된 폴더
OUTPUT_FOLDER = "output"  # 결과를 저장할 폴더
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "conversations_2k_multi.jsonl")  # 결과 파일 경로
ERROR_LOG_FILE = os.path.join(OUTPUT_FOLDER, "error_log.txt")  # 결과 파일 경로

# 첫 5턴 고정 질문 리스트
FIXED_QUESTIONS = [
    "이 파일의 내용에 대해 3문장으로 요약해 주세요.",
    "이 파일의 내용에 대해 7문장으로 요약해 주세요.",
    "이 파일의 노드들에 대해 설명해 주세요.",
    "이 파일의 노드들의 계층에 대해 설명해 주세요.",
    "이 파일의 노드들 간 관계를 고려하여 흐름에 대해 설명해 주세요."
]

# 이미지 파일을 Base64로 인코딩하는 함수
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
# 토큰 수 계산
def calculate_tokens(messages):
    encoding = tiktoken.encoding_for_model("gpt-4o")
    return sum(len(encoding.encode(message["content"])) for message in messages)

# OpenAI API 요청 함수 (GPT-4o + 이미지 지원)
def generate_conversation(image_path, json_data, filename):
    # 이미지 파일 Base64 인코딩
    print(f"image file path: {image_path}")
    image_data = encode_image(image_path)

    system_message = {
        "role": "system",
        "content": "주어진 이미지 및 JSON 데이터를 분석하여 10개의 질문과 10개의 응답으로 구성된 대화 데이터를 생성하는 AI입니다. "
                    "처음 5개의 대화에는 다음 질문을 포함해야 합니다.\n"
                    "<image>\\n- 이 파일의 내용에 대해 3문장으로 요약해 주세요.\n"
                    "- 이 파일의 내용에 대해 7문장으로 요약해 주세요.\n"
                    "- 이 파일의 노드들에 대해 설명해 주세요.\n"
                    "- 이 파일의 노드들의 계층에 대해 설명해 주세요.\n"
                    "- 이 파일의 노드들 간 관계를 고려하여 흐름에 대해 설명해 주세요.\n"

                    "추가로 생성할 대화 데이터는 5개의 질문과 5개의 응답으로 구성합니다. 여기에서는 5개 질문을 추가로 생성합니다. 대화의 질문은 전달된 파일의 내용이나 관계를 충분히 고려하고 파일의 내용에 근거해서 생성해 주세요.\n"
                    "응답은 다음 JSON 형식으로 제공해야 합니다:\n"
                    "{\n"
                    f"  \"id\": \"{filename.replace('.png', '')}\",\n"
                    f"  \"image\": \"{filename}\",\n"
                    "  \"conversations\": [\n"
                    "    {\n"
                    "      \"from\": \"human\",\n"
                    "      \"value\": \"사용자 질문\"\n"
                    "    },\n"
                    "    {\n"
                    "      \"from\": \"gpt\",\n"
                    "      \"value\": \"AI 응답\"\n"
                    "    }\n"
                    "  ]\n"
                    "}\n"
    }

    user_message = {
        "role": "user",
        "content": f"<image>\\n다음 JSON 데이터와 이미지를 분석하고 내용을 요약해 주세요:\n\n"
                   f"JSON 데이터:\n{json.dumps(json_data, ensure_ascii=False, indent=4)}\n\n"
                   f"이미지:\n{image_path}"
    }

    messages = [system_message, user_message]

    # 토큰 수 출력
    print(f"System message token count: {calculate_tokens([system_message])}")
    print(f"User message token count: {calculate_tokens([user_message])}")

    # 토큰 제한 확인
    max_tokens = 128000  # 모델의 최대 컨텍스트 길이
    if calculate_tokens(messages) > max_tokens:
        raise ValueError("메시지가 너무 길어 모델의 최대 컨텍스트 길이를 초과합니다.")

    response = client.chat.completions.create(model="gpt-4o", messages=messages)

    # # GPT 응답 처리
    response_content = response.choices[0].message.content
    # print(f"GPT Response Content: {response_content}")
    clean_content = response_content.replace("```", "").replace("json", "") # 리턴된 문자열에서 json 규격을 벗어난 문자들을 제거

    if not clean_content.strip():
        error_message = f"Error: GPT response is empty for file {filename}.\n"
        print(error_message)
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as error_log:
            error_log.write(error_message)
        return None

    try:
        conversation_data = json.loads(clean_content)
    except json.JSONDecodeError as e:
        error_message = f"Error decoding JSON from GPT response for file {filename}: {e}\n"
        print(error_message)
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as error_log:
            error_log.write(error_message)
        return None
    
    # # 첫 번째 대화의 value에 "<image>\n이 이미지는 무엇을 설명하고 있나요?" 추가
    if "conversations" in conversation_data and len(conversation_data["conversations"]) > 0:
        conversation_data["conversations"][0]["value"] = "<image>\n이 파일의 내용에 대해 3문장으로 요약해 주세요."
    
    # return response.choices[0].message.content
    return conversation_data

# 결과 폴더 생성
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# JSON 데이터 파일 목록 가져오기
json_files = [f for f in os.listdir(JSON_FOLDER) if f.endswith(".json")]
all_conversations = []

# JSON 파일 시작

# with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
#     output_file.write("[\n")

# 에러 로그 파일 초기화
with open(ERROR_LOG_FILE, "w", encoding="utf-8") as error_log:
    error_log.write("Error Log:\n")    

# 파일별 대화 데이터 생성
for json_file in json_files:
    json_path = os.path.join(JSON_FOLDER, json_file)

    with open(json_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    image_name = json_data.get("file_name", "")

    image_path = os.path.join(IMAGE_FOLDER, image_name)

    if not os.path.exists(image_path):
        error_message = f"Error: Image file {image_name} not found for {json_file}.\n"
        print(error_message)
        # 에러 로그에 기록
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as error_log:
            error_log.write(error_message)
        continue

    conversation_data = generate_conversation(image_path, json_data, image_name)
    # cleaned_json = conversation_data.replace("```", "").replace("json", "") # 리턴된 문자열에서 json 규격을 벗어난 문자들을 제거
    # print(cleaned_json)

    # JSON 형식 검증
    if not conversation_data:
        print(f"Error: GPT response for {json_file} is empty.")
        continue
    # try:
    #     conversation_data = json.loads(cleaned_json)
    # except json.JSONDecodeError as e:
    #     error_message = f"Error decoding JSON from GPT response for {json_file}: {e}\n"
    #     print(error_message)
    #     with open(ERROR_LOG_FILE, "a", encoding="utf-8") as error_log:
    #         error_log.write(error_message)
    #     continue
        
    # 결과를 바로 JSON 파일에 저장
    with open(OUTPUT_FILE, "a", encoding="utf-8") as output_file:
        output_file.write(json.dumps(conversation_data, ensure_ascii=False) + ",\n")

    print(f"{json_path} QA 생성 완료.")

# 모든 결과를 하나의 JSON 파일로 저장
# with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
#     json.dump(all_conversations, output_file, ensure_ascii=False, indent=4)

# JSON 파일 끝
# with open(OUTPUT_FILE, "a", encoding="utf-8") as output_file:
#     output_file.write("]\n")

print("Batch processing completed. All results saved in 'conversations.json'.")
