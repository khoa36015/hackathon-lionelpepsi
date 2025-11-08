from api import app

print("All checkin routes:")
for rule in app.url_map.iter_rules():
    if 'checkin' in str(rule):
        print(f"  {rule} -> {rule.methods}")

