from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Review, ShoppingCart, CustomerOrder,Rate
from django.db.models import Q, Sum, Count
import urllib
import xmltodict
import datetime
from operator import itemgetter

from django.views import generic
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import get_messages

from django.urls import reverse
from django.http import HttpResponseRedirect

from django.db import IntegrityError

from .forms import SearchForm, UserRegistrationForm, ProfileForm, LoginForm

isbn_list_of_dicts = []

def home(request):
    #TODO: add functionality
    return render(request, 'bookstore/index.html')


def search(request):
    #TODO: add response to search function
    print ("here")
    """Book search based on authors, and/or publisher, and/or title, and/or subjec"""
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # print (request.GET['search_value'])
        isbn_list_of_dicts = []

        # check whether it's valid:
        if form.is_valid():
            temp_dict = {}
            print (form.cleaned_data)
            search_values = form.cleaned_data['search_value'].split(" ")
            search_values = list(filter(None, search_values))
            print ("Search form")
            print (search_values)

            isbn_list_of_dicts = query(search_values)

    print (isbn_list_of_dicts)
    request.session['isbn_list_of_dicts'] = isbn_list_of_dicts
    request.session.modified = True
    return render(request, 'bookstore/search_results.html', {'books': request.session['isbn_list_of_dicts']})

def search_filter_author(request):
    return render(request, 'bookstore/search_filter_author.html', {'books': request.session['isbn_list_of_dicts']})

def search_filter_year(request):
    return render(request, 'bookstore/search_filter_year.html', {'books': request.session['isbn_list_of_dicts']})

def search_specific(request, key, specified):
    search_values = [specified]
    isbn_list_of_dicts = query(search_values)

    print (isbn_list_of_dicts)
    request.session['isbn_list_of_dicts'] = isbn_list_of_dicts
    request.session.modified = True
    return render(request, 'bookstore/search_filter_year.html', {'books': request.session['isbn_list_of_dicts']})

def query(search_values):
    # Get isbn hit count from book table
    isbn_list_of_dicts = []
    temp_dict = {}
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
            if j in temp_dict:
                temp_dict[j][0] += 1
            else:
                temp_dict[j] = [1]
    print (temp_dict)

    for i in temp_dict:
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
            temp_dict[i].append(book_img)

    for i in temp_dict:
        temp_dict[i].append(get_object_or_404(Book, isbn10=i))
    for i in temp_dict:
        append_this_dict = {'isbn10': i, 'data': {  'hits': temp_dict[i][0],
                                                    'url': temp_dict[i][1],
                                                    'title': temp_dict[i][2].title,
                                                    'publisher': temp_dict[i][2].publisher,
                                                    'year': temp_dict[i][2].years,
                                                    'author': temp_dict[i][2].author}}
        isbn_list_of_dicts.append(append_this_dict)
    return isbn_list_of_dicts

def book_details(request, bid, sort_newest=False):
    book = get_object_or_404(Book, isbn10=bid)
    username = request.user.username
    user = User.objects.get(username=username)

    #get total rating for each review
    r = Rate.objects.filter(isbn13=book).values('rated').annotate(Sum('rating'))
    
    #get list of reviews for book
    reviews= Review.objects.filter(isbn13=book).order_by('review_date').reverse()
        
    #Get score of book
    avg_score = 0
    uscore = 5
    if reviews:
        for review in reviews:
            avg_score += review.review_score
        avg_score = avg_score/len(reviews)
    rounded_score = round(avg_score)
    uri = "http://www.goodreads.com/book/title?format=xml&key=VZTtD5ycbJ7Azy1BnZmg&isbn=%s" %(str(bid))
    try:
        f = urllib.request.urlopen(uri)
        data = f.read()
        f.close()
        data = xmltodict.parse(data)
        #print (data['GoodreadsResponse']['book']['image_url'])
        book_img = data['GoodreadsResponse']['book']['image_url']
    except:
        print ('excepted yo')
        book_img = 'http://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png'

    if not sort_newest:
        review_list_best = []
        reviews = Review.objects.filter(isbn13=book)
        for review in reviews:
            for rate in r:
                if review.id == rate['rated']:
                    item = {'login_name': review.login_name,
                            'id': review.id,
                            'review_score': review.review_score,
                            'review_text': review.review_text,
                            'review_date': review.review_date,
                            'total_rating': rate['rating__sum'],
                    }
                    review_list_best.append(item)
        #reviews = sorted(review_list_best, key=lambda k: k['total_rating'])
        reviews = sorted(review_list_best, key=itemgetter('total_rating'), reverse=True)


    return render(request, 'bookstore/book_details.html', {'book': book, 'book_img': book_img, 'avg_score': rounded_score, 'uscore':uscore, 'reviews':reviews, 'review_ratings':r})

def review_filter_newest(request, bid):
    rend = book_details(request, bid, sort_newest=True)
    return rend

def review_filter_best(request, bid):
    rend = book_details(request, bid)
    return rend

@login_required
def review(request, bid):
    book = get_object_or_404(Book, isbn10=bid)
    username = request.user.username
    user = User.objects.get(username=username)
    full_name = request.user.first_name + ' ' + request.user.last_name


    #TODO: Check what score was submitted
    uscore = int(request.POST['ratinga'])
    #Check if review was submitted
    ureview = request.POST['ureview']
    if ureview == '':
        book = get_object_or_404(Book, isbn10=bid)
        uri = "http://www.goodreads.com/book/title?format=xml&key=VZTtD5ycbJ7Azy1BnZmg&isbn=%s" %(str(bid))
        uscore = 5
        reviews = Review.objects.filter(isbn13=book.isbn13)
        r = Rate.objects.filter(isbn13=book).values('rated').annotate(Sum('rating'))
        avg_score = 0
        if reviews:
            for review in reviews:
                avg_score += review.review_score
            avg_score = avg_score/len(reviews)
            rounded_score = round(avg_score)
        try:
            f = urllib.request.urlopen(uri)
            data = f.read()
            f.close()
            data = xmltodict.parse(data)
            #print (data['GoodreadsResponse']['book']['image_url'])
            book_img = data['GoodreadsResponse']['book']['image_url']
        except:
            print ('excepted yo')
            book_img = 'http://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png'

        return render(request, 'bookstore/book_details.html', {'book': book, 'book_img': book_img, 'avg_score':rounded_score, 'uscore':uscore, 'error_message':"Please enter a valid review!", 'reviews':reviews, 'review_ratings': r})

    #if user has valid review, insert into Review table
    try:
        review = Review(login_name=user, isbn13=book, review_score=uscore, review_text=ureview, review_date=datetime.date.today())
        review.save()
    except IntegrityError as e:
        messages.add_message(request, messages.INFO, "You already reviewed this item!")
       
        return HttpResponseRedirect(reverse('bookstore:book_details', args=(bid,)))

    return render(request, 'bookstore/review_success.html', {'book':book})

@login_required
def add_to_cart(request, bid):
    book = get_object_or_404(Book, isbn10=bid)

    #TODO: Check if user is logged in, get user id
    username = request.user.username
    #Insert to shopping cart
    try:
        shopcart = ShoppingCart(login_name=User.objects.get(username=username), isbn13=book, num_order=1,order_date=datetime.date.today())
        shopcart.save()
    except IntegrityError as e:
        # messages.error(request, "You already have this book in your cart!")
        messages.add_message(request, messages.ERROR, "You already have this book in your cart!")
       
        return HttpResponseRedirect(reverse('bookstore:book_details', args=(bid,)))

    return render(request, 'bookstore/index.html', {'book_in_cart': book.title})

@login_required
def rate_user_review(request, bid, rid):
    username = request.user.username
    user = User.objects.get(username=username)

    book = Book.objects.get(isbn10=bid)
    review = Review.objects.get(id=rid)

    rating = request.POST['rate']
    
    try:
        if user == review.login_name:
            raise Exception("hoho")
        rate = Rate(rater=user,rated=review,rating=int(rating),isbn13=book)
        rate.save()
    except IntegrityError as e:
        messages.add_message(request, messages.WARNING, "You already have rated this review!")
        print("hehyy")
        return HttpResponseRedirect(reverse('bookstore:book_details', args=(bid,)))
    except Exception as ee:
        messages.add_message(request, messages.WARNING, "You cannot rate your own review.")
        print("hehyy")
        return HttpResponseRedirect(reverse('bookstore:book_details', args=(bid,)))

    return HttpResponseRedirect(reverse("bookstore:book_details", args=(bid,)))


class AccountView(View):
    template_name = 'bookstore/account.html'

    def get(self, request):
        return render(request, self.template_name)

class BookstoreAdminView(UserPassesTestMixin, View):
    raise_exception = True
    template_name = 'bookstore/bookstore-admin.html'

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        return render(request, self.template_name)

class CartView(View):
    template_name = 'bookstore/cart.html'

    def get(self, request):
        user = request.user
        cart = ShoppingCart.objects.filter(login_name=user.id)
        books_in_cart = Book.objects.filter(isbn13__in=cart.values('isbn13'))
        orders = CustomerOrder.objects.filter(login_name=user.id)
        books_ordered = Book.objects.filter(isbn13__in=orders.values('isbn13'))

        content = {'cart':cart, 'books_in_cart':books_in_cart, 'orders': orders, 'books_ordered':books_ordered}
        img_dict = {}
        for item in cart:
            for b in books_in_cart:
                if item.isbn13.isbn13 == b.isbn13:
                    try:
                        uri = "http://www.goodreads.com/book/title?format=xml&key=VZTtD5ycbJ7Azy1BnZmg&isbn=%s" %(str(b.isbn10))
                        f = urllib.request.urlopen(uri)
                        data = f.read()
                        f.close()
                        data = xmltodict.parse(data)
                        #print (data['GoodreadsResponse']['book']['image_url'])
                        book_img = data['GoodreadsResponse']['book']['image_url']
                    except:
                        print ('excepted yo')
                        book_img = 'http://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png'
                    finally:
                        img_dict[b.isbn13] = book_img
        content['img_dict'] = img_dict
        return render(request, self.template_name, content)

class OrderView(View):

    def post(self, request):
        username = request.user.username
        print(request.POST)
        for k,v in request.POST.items():
            if "Submit" in request.POST.keys():
                if len(k)== 13:
                    user = User.objects.get(username=username)
                    book = Book.objects.get(isbn13=k)
                    order_status = "Processed"
                    order = CustomerOrder(login_name=user, isbn13=book, num_order=int(v), order_date=datetime.date.today()+datetime.timedelta(1), order_status=order_status)
                    order.save()

                    ShoppingCart.objects.filter(login_name=user).delete()
            else:
                user = User.objects.get(username=username)
                ShoppingCart.objects.filter(login_name=user, isbn13=request.POST['remove']).delete()

        return HttpResponseRedirect(reverse('bookstore:cart'))

    def get(self, request):
        return HttpResponseRedirect(reverse('bookstore:cart'))

class RegistrationFormView(View):
    user_form_class = UserRegistrationForm
    profile_form_class = ProfileForm
    template_name = 'bookstore/registration-form.html'

    # display blank form
    def get(self, request):
        user_form = self.user_form_class(None)
        profile_form = self.profile_form_class(None)
        return render(request, self.template_name, {
            'forms': [user_form, profile_form]
        })

    # process form data
    def post(self, request):
        user_form = self.user_form_class(request.POST)
        profile_form = self.profile_form_class(request.POST)
        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save(commit=False)

            # cleaned (normalized) data
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            user.set_password(password)
            user.save()

            user.profile.credit_card_number = profile_form.cleaned_data['credit_card_number']
            user.profile.mailing_address = profile_form.cleaned_data['mailing_address']
            user.profile.phone_number = profile_form.cleaned_data['phone_number']
            user.profile.save()

            # returns User object if credentials are correct
            user = authenticate(username=username, password=password)



            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('bookstore:home')

        return render(request, self.template_name, {
            'forms': [user_form, profile_form]
        })

class LogoutView(View):
    template_name = 'bookstore/logout.html'

    def get(self, request):
        logout(request)
        return render(request, self.template_name)


class LoginFormView(View):
    form_class = LoginForm
    template_name = 'bookstore/login-form.html'

    # display blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # process form data
    def post(self, request):
        form = self.form_class(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        # returns User object if credentials are correct
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(self.request.GET.get('next', 'bookstore:home'))

        return render(request, self.template_name, {
            'form': form,
            'error_message': 'The username and password provided do not match'
        })
