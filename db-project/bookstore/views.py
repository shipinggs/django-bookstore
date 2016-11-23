from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Book
import urllib
import xmltodict
from .forms import SearchForm
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

def search(request):
    #TODO: add response to search function
    """Book search based on authors, and/or publisher, and/or title, and/or subjec"""
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        isbn_dict = {}

        # check whether it's valid:
        if form.is_valid():
            isbn_dict = {}
            img_dict = {}
            search_values = form.cleaned_data['search_value'].split(" ")
            search_values = list(filter(None, search_values))
            print (search_values)

            # Get isbn hit count from book table
            for i in search_values:
                temp = []
                search_title = Book.objects.filter(title__icontains=i)
                search_author = Book.objects.filter(author__icontains=i)
                search_publisher = Book.objects.filter(publisher__icontains=i)
                search_subject = Book.objects.filter(book_subject__icontains=i)

                temp.extend(search_title.values_list('isbn10', flat=True))
                temp.extend(search_author.values_list('isbn10', flat=True))
                temp.extend(search_publisher.values_list('isbn10', flat=True))
                temp.extend(search_subject.values_list('isbn10', flat=True))

                for j in temp:
                    if j in isbn_dict:
                        isbn_dict[j] += 1
                    else:
                        isbn_dict[j] = 1
            print (isbn_dict)

            for i in isbn_dict:
                uri = "http://www.goodreads.com/book/title?format=xml&key=VZTtD5ycbJ7Azy1BnZmg&isbn=%s"%(str(i))
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
                finally:
                    img_dict[i] = book_img

    print (img_dict)
    return render(request, 'bookstore/search_results.html', {'books': isbn_dict, 'book_imgs': img_dict})

def register(request):
    #TODO: add functionality
    return HttpResponse('<h1>You are at register page</h1>')

def book_details(request, bid):
    book = get_object_or_404(Book, isbn10=bid)

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
    
    rating = 4
    return render(request, 'bookstore/book_details.html', {'book': book, 'book_img': book_img, 'rating': rating})

def review(request, bid):
    book = get_object_or_404(Book, bid=bid)
    return HttpResponse("Standby review")

def add_to_cart(request, bid):
    return HttpResponse('<h1>You are adding book to shopping cart</h1>')