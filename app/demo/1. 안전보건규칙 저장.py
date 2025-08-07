import json

from dotenv import load_dotenv
from modules.open_law.api import 안전보건규칙

load_dotenv()

data = 안전보건규칙("JSON")

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Data saved to data.json")