from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_KEY = "AIzaSyDZnHjzFxl8nw8oIvjy-f3-rQBSP_UKc28"
CX = "c6066959091404230"

service = build("customsearch", "v1", developerKey=API_KEY)

try:
    res = service.cse().list(q="site:boards.greenhouse.io remote data", cx=CX, num=10).execute()
    print("OK, items:", len(res.get("items", [])))
except HttpError as e:
    print("HTTP ERROR:", e.status_code)
    print(e.content.decode("utf-8"))
