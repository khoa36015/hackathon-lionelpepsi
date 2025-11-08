from data import bao_tang_chung_tich

PHAN_LOAI = bao_tang_chung_tich.get("phan_loai", {})

locations = ["Khu Trưng Bày Trong Nhà", "Khu Trưng Bày Ngoài Trời"]

all_photos = PHAN_LOAI.get("anh", [])
all_artifacts = PHAN_LOAI.get("di_vat", [])

print(f"Total photos: {len(all_photos)}, artifacts: {len(all_artifacts)}")
print(f"Selected locations: {locations}")
print()

# Filter photos
photos = []
for photo in all_photos:
    photo_copy = photo.copy()
    # Assign location based on photo type/name
    if "quốc tế" in photo.get("ten", "").lower() or "phóng viên" in photo.get("ten", "").lower():
        photo_copy["dia_diem"] = "Khu Trưng Bày Ảnh Quốc Tế"
    else:
        photo_copy["dia_diem"] = "Khu Trưng Bày Trong Nhà"
    
    print(f"Photo '{photo.get('ten')}' -> {photo_copy['dia_diem']}, in locations: {photo_copy['dia_diem'] in locations}")
    
    if photo_copy["dia_diem"] in locations:
        photos.append(photo_copy)

print()

# Filter artifacts
artifacts = []
for artifact in all_artifacts:
    artifact_copy = artifact.copy()
    # Assign location based on artifact type
    if any(keyword in artifact.get("ten", "").lower() for keyword in ["máy bay", "xe tăng", "trực thăng"]):
        artifact_copy["dia_diem"] = "Khu Trưng Bày Ngoài Trời"
    elif "tra tấn" in artifact.get("ten", "").lower() or "tù binh" in artifact.get("ten", "").lower():
        artifact_copy["dia_diem"] = "Phòng Trà Tân"
    else:
        artifact_copy["dia_diem"] = "Khu Trưng Bày Trong Nhà"
    
    print(f"Artifact '{artifact.get('ten')}' -> {artifact_copy['dia_diem']}, in locations: {artifact_copy['dia_diem'] in locations}")
    
    if artifact_copy["dia_diem"] in locations:
        artifacts.append(artifact_copy)

print()
print(f"Filtered photos: {len(photos)}, artifacts: {len(artifacts)}")
print()
print("Photos:")
for p in photos:
    print(f"  - {p.get('ten')} (ID: {p.get('id')})")
print()
print("Artifacts:")
for a in artifacts:
    print(f"  - {a.get('ten')} (ID: {a.get('id')})")

