import requests, json,os, random, string

FILE_DIR = os.path.dirname(os.path.realpath(__file__))

categories = ["arts","accounting","business","essay","journal","memoir","nonfiction","reference","help","science","society","textbook"]

def get_json(cat):
    data = ""
    with open("%s/isbndb-data-new-random.json"%FILE_DIR, "rb") as file_open:
        x = requests.get("http://isbndb.com/api/v2/json/Y7GX3B6X/books?q={}".format(cat))
        # random_category = random.choice(categories)
        # x = requests.get("http://isbndb.com/api/v2/json/Y7GX3B6X/books?q={}&i=book_summary".format(cat))
        # x = requests.get("http://isbndb.com/api/v2/json/Y7GX3B6X/books?q={}&i=book_notes".format(cat))
        x = requests.get("http://isbndb.com/api/v2/json/Y7GX3B6X/books?q={}&i=publisher_name".format(cat))

        print x
        if 'error' in x.json():
            print False
            return False
        data = json.load(file_open)
        data["data"].extend(x.json()["data"])

    with open("%s/isbndb-data-new-random.json"%FILE_DIR, "w") as file_open:
        file_open.write(json.dumps(data, indent=4, sort_keys=True))

    return True

counter = 0
# for i in range (100):
# while counter < 100:
#     print counter
#     if get_json():
#         counter += 1

for i in categories:
    get_json(i)
