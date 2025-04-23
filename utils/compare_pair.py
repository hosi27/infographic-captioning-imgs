import os

# 폴더 경로 설정
base_path = "test_data"
img_folder = os.path.join(base_path, "img_filtered")
json_folder = os.path.join(base_path, "json_filtered")

# 파일 이름에서 확장자 제거 후 set으로 수집
img_names = {os.path.splitext(f)[0] for f in os.listdir(img_folder) if os.path.isfile(os.path.join(img_folder, f))}
json_names = {os.path.splitext(f)[0] for f in os.listdir(json_folder) if os.path.isfile(os.path.join(json_folder, f))}

# 비교
both_exist = img_names & json_names
only_img = img_names - json_names
only_json = json_names - img_names

# 출력
print("✅ 이미지 + JSON 모두 존재하는 파일:")
for name in sorted(both_exist):
    print(f"  - {name}")

print("\n❌ 이미지만 있고 JSON 없는 파일:")
for name in sorted(only_img):
    print(f"  - {name}")

print("\n❌ JSON만 있고 이미지 없는 파일:")
for name in sorted(only_json):
    print(f"  - {name}")
