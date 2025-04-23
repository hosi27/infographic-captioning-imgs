import os

# 파일이 저장된 폴더 경로
folder_path = "test_data/kt/image"

# 존재해야 하는 파일 번호 (0001 ~ 1000)
expected_numbers = set(f"{i:04d}" for i in range(1, 1001))

# 폴더 내 실제 파일 번호 추출
existing_numbers = set()

for filename in os.listdir(folder_path):
    name, ext = os.path.splitext(filename)  # 파일명과 확장자 분리
    if name.isdigit() and name in expected_numbers:  # 숫자로 된 파일만 확인
        existing_numbers.add(name)

# 누락된 파일 번호 찾기
missing_numbers = sorted(expected_numbers - existing_numbers)

# 결과 출력
if missing_numbers:
    print(f"누락된 파일 개수: {len(missing_numbers)}개")
    print("누락된 파일 번호:", missing_numbers)
else:
    print("모든 파일이 존재합니다.")
