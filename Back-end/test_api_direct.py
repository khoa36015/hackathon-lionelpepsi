import sys
sys.path.insert(0, '.')

from api import app, PHAN_LOAI

print(f"PHAN_LOAI keys: {list(PHAN_LOAI.keys())}")
print(f"Photos: {len(PHAN_LOAI.get('anh', []))}")
print(f"Artifacts: {len(PHAN_LOAI.get('di_vat', []))}")

with app.test_client() as client:
    response = client.post('/api/tours/items-by-location', 
                          json={"locations": ["Khu Trưng Bày Trong Nhà", "Khu Trưng Bày Ngoài Trời"]})
    print(f"\nResponse status: {response.status_code}")
    print(f"Response data: {response.get_json()}")

