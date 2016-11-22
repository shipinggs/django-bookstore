import json, os, random

FILE_DIR = os.path.dirname(os.path.realpath(__file__))

insert_values = ""
with open("%s/isbndb-data.json"%FILE_DIR, "rb") as file_open:
    data = json.load(file_open)
    for i in data["data"]:
        authors = ""
        for j in i["author_data"]:
            authors+= j["name"] + " "
        price = round(random.uniform(50.0, 200.0),2)
        book_type = random.choice(["hardcover","paperback"])
        book_subject = ""
        if len(i["subject_ids"]) > 0:
            book_subject = i["subject_ids"][0]

        insert_values += "INSERT INTO django_db.books VALUES ("
        insert_values+= "'" + i["isbn13"] + "'"
        insert_values+= ",'" + i["isbn10"] + "'"
        insert_values+= ",'" + i["title"] + "'"
        insert_values+= ",'" + authors + "'"
        insert_values+= ",'" + i["publisher_name"] + "'"
        insert_values+= "," + str(0)
        insert_values+= "," + str(5)
        insert_values+= "," + str(price)
        insert_values+= ",'" + book_type + "'"
        insert_values+= ",'" + i["title"] + "'"
        insert_values+= ",'" + book_subject + "'"
        insert_values+= ");\n"
with open("%s/books.sql"%FILE_DIR, "a") as file_open:
    file_open.write(insert_values)
