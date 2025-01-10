import os

# 변경할 파일이 있는 폴더 경로
folder_path = "temp"

# 파일명 변경 범위 설정
start_old = 1  # 기존 파일 시작 번호 (0200)
end_old = 350  # 기존 파일 끝 번호 (0230)
start_new = 647  # 새 파일 시작 번호 (0300)

# 폴더 내 파일 목록 조회
for old_num in range(start_old, end_old + 1):
    old_prefix = f"{old_num:04d}."  # 기존 파일명 패턴 (0200. 확장자)
    new_prefix = f"{start_new + (old_num - start_old):04d}."  # 새 파일명 패턴 (0300. 확장자)

    for filename in os.listdir(folder_path):
        if filename.startswith(old_prefix):
            old_path = os.path.join(folder_path, filename)
            new_filename = filename.replace(old_prefix, new_prefix, 1)
            new_path = os.path.join(folder_path, new_filename)

            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_filename}")

print("파일명 변경 완료!")
