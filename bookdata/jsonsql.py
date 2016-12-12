import json
from pprint import pprint
import re
import MySQLdb
import random

testFile = open("isbndb-data-new-random.json")
data = json.load(testFile)

#pprint(data)
db = MySQLdb.connect(host="localhost", user="root", passwd="password", db="django_db")
cur = db.cursor()

l = []
for i in range(len(data['data'])):
    # print i
    isbn13 = data['data'][i]['isbn13']
    isbn10 = data['data'][i]['isbn10']
    title = data['data'][i]['title']
    
    try:
        author = data['data'][i]['author_data'][0]['name']
    except:
        author = 'John Doe'
    publisher = data['data'][i]['publisher_text']
    try:
        year = int(re.search(r'\d+', data['data'][i]['edition_info']).group())

    except:
        try:
            year = int(re.search(r'\d+', data['data'][i]['publisher_text']).group())
        except:
            year = random.randint(1970,2014)
    num_copies = 1
    price = round(random.uniform(20.0, 80.0), 2)
    try:
        book_format = re.search(r'Hardcover', data['data'][i]['edition_info']).group()
    except:
        book_format = 'Paperback'
    keyword = (data['data'][i]['summary'][:250] + '...') if len(data['data'][i]['summary'])> 250 else data['data'][i]['summary']
    try:
        book_subject = data['data'][i]['subject_ids'][0]
    except:
        book_subject = 'General'

    statement = "INSERT INTO book VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        cur.execute(statement, (isbn13,isbn10,title, author,publisher,year,num_copies,price,book_format,keyword,book_subject))
        db.commit()
    except:
        db.rollback()


db.close()




##import isbnlib
##
##isbn = '9788177581805'
##
##book = isbnlib.meta(isbn)
##
##title = book['Title']
##authors = book['Authors']
