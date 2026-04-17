import json

with open("logs.json", "r", encoding="utf-8") as archivo:
    logs = json.load(archivo)

for log in logs:
    if log["estado"] == "FAILED":
        print(f"Intento fallido desde IP: {log['ip']}")
