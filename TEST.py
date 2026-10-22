import requests

HEADERS = {
    "Accept": "application/json",
    "Authorization": "Bearer oDKEPywvbxR5qfTA"
}

try:
    resp = requests.get("http://176.187.5.27:15295/elo", headers=HEADERS)
    resp.raise_for_status()
    collection = resp.json() # .get("rank", None)
    print(collection)
except Exception as e:
    print(e)
