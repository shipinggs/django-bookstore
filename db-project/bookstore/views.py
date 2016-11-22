from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Books
import urllib
import xmltodict

def account(request):
    #TODO: add functionality
    return HttpResponse('<h1>You are at account page</h1>')

def admin(request):
    #TODO: add functionality
    return HttpResponse('<h1>You are at admin page</h1>')

def cart(request):
    #TODO: add functionality
    return HttpResponse('<h1>You are at cart page</h1>')

def home(request):
    #TODO: add functionality
    return render(request, 'bookstore/home.html')

def login(request):
    #TODO: add functionality
    return HttpResponse('<h1>You are at login page</h1>')

def register(request):
    #TODO: add functionality
    return HttpResponse('<h1>You are at register page</h1>')

def book_details(request, bid):
    book = get_object_or_404(Books, isbn10=bid)

    uri = "http://www.goodreads.com/book/title?format=xml&key=VZTtD5ycbJ7Azy1BnZmg&isbn=%s" %(str(bid))
    try:
        f = urllib.request.urlopen(uri)
        data = f.read()
        f.close()

        data = xmltodict.parse(data)
        print (data['GoodreadsResponse']['book']['image_url'])
        book_img = data['GoodreadsResponse']['book']['image_url']
    except:
        print ('excepted yo')
        book_img = 'http://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png'
    return render(request, 'bookstore/book_details.html', {'book': book, 'book_img': book_img})
