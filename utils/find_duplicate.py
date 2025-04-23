import os
from PIL import Image
import imagehash

# 이미지가 저장된 폴더 경로
folder_path = "imgs/06. 사회/난이도 2"

# 중복 이미지 저장 리스트
duplicate_images = []

# 이미지 해시 저장 딕셔너리
hash_dict = {}

# 폴더 내 이미지 파일 처리
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

    # 이미지 파일만 처리
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
        try:
            # 이미지 열기
            img = Image.open(file_path)
            
            # 이미지 해시 계산 (Perceptual Hash)
            img_hash = imagehash.phash(img)
            
            # 해시값이 이미 존재하면 중복으로 간주
            if img_hash in hash_dict:
                print(f"중복 이미지 발견: {filename} <-> {hash_dict[img_hash]}")
                duplicate_images.append((filename, hash_dict[img_hash]))
            else:
                hash_dict[img_hash] = filename
        
        except Exception as e:
            print(f"이미지 처리 오류: {filename}, 오류: {e}")

print("\n중복 검사 완료!")
if duplicate_images:
    print("중복된 이미지 목록:")
    for dup in duplicate_images:
        print(f" - {dup[0]} <-> {dup[1]}")
else:
    print("중복된 이미지가 없습니다.")
