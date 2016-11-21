import requests, json,os

FILE_DIR = os.path.dirname(os.path.realpath(__file__))

categories = ["arts","business","computers","education","genres","health","regions","science","society"]

def get_json():
    data = ""
    with open("%s/isbndb-data.json"%FILE_DIR, "rb") as file_open:
        x = requests.get("http://isbndb.com/api/v2/json/9IO83L75/books?q=business")
        data = json.load(file_open)
        data["data"].extend(x.json()["data"])

    with open("%s/isbndb-data.json"%FILE_DIR, "w") as file_open:
        file_open.write(json.dumps(data, indent=4, sort_keys=True))

for i in range (100):
    get_json()
