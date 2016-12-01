from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Review, ShoppingCart, CustomerOrder
from django.db.models import Q
import urllib
import xmltodict
import datetime

from django.views import generic
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User

from django.urls import reverse
from django.http import HttpResponseRedirect

from .forms import SearchForm, UserRegistrationForm, ProfileForm, LoginForm

isbn_list_of_dicts = []

def home(request):
    #TODO: add functionality
    if request.user.is_authenticated():
        recommended = query(request.user.id, 'recommend')
        request.session['recommended'] = recommended
        request.session.modified = True
    # test =  query(request.user.id, 'recommend')
        return render(request, 'bookstore/index.html', {'books': request.session['recommended']})
    else:
        return render(request, 'bookstore/index.html', {'books': ''})


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
            search_values = form.cleaned_data['search_value'].split(" ")
            search_values = list(filter(None, search_values))
            print (search_values)


            isbn_list_of_dicts = query(search_values, 'all')
    if len(isbn_list_of_dicts) == 0:
        return render(request, 'bookstore/search_results.html', {'books': request.session['isbn_list_of_dicts'], 'status': 'No results could be found :('})
    print (isbn_list_of_dicts)
    request.session['isbn_list_of_dicts'] = isbn_list_of_dicts
    request.session.modified = True
    return render(request, 'bookstore/search_results.html', {'books': request.session['isbn_list_of_dicts'] , 'status': 'Search results for "%s"'%(' '.join(search_values))})

def search_filter_author(request):
    return render(request, 'bookstore/search_filter_author.html', {'books': request.session['isbn_list_of_dicts']})

def search_filter_year(request):
    return render(request, 'bookstore/search_filter_year.html', {'books': request.session['isbn_list_of_dicts']})

def search_filter_score(request):
    return render(request, 'bookstore/search_filter_score.html', {'books': request.session['isbn_list_of_dicts']})

def search_specific(request, key, specified):
    search_values = [specified]
    isbn_list_of_dicts = query(search_values, key)

    print (isbn_list_of_dicts)
    request.session['isbn_list_of_dicts'] = isbn_list_of_dicts
    request.session.modified = True
    return render(request, 'bookstore/search_results.html', {'books': request.session['isbn_list_of_dicts'], 'status': 'Search results for "%s" under %s'%(' '.join(search_values), key)})

def query(search_values, query_type):
    # Get isbn hit count from book table
    isbn_list_of_dicts = []
    temp_dict = {}

    if query_type == 'recommend':
        temp = []
        # get all orders of the current user
        search_user_books = CustomerOrder.objects.filter(login_name=search_values)
        # get all the isbn13 of these orders
        current_user_books = []
        current_user_books.extend(search_user_books.values_list('isbn13', flat=True))
        print (current_user_books)
        other_users = []
        for i in current_user_books:
            temp_users = CustomerOrder.objects.filter(isbn13=i)
            other_users.extend(temp_users.values_list('login_name', flat=True))

        print (other_users)
        other_users = list(set(other_users))
        if search_values in other_users:
            other_users.remove(search_values)
        temp_isbn13 = []
        print (other_users)
        for i in other_users:
            temp_other_user_books = CustomerOrder.objects.filter(login_name=i)
            temp_isbn13.extend(temp_other_user_books.values_list('isbn13', flat=True))

        for i in temp_isbn13:
            if i not in current_user_books:
                book = Book.objects.get(isbn13=i)
                temp.append(book.isbn10)

    else:
        for i in search_values:
            temp = []
            if query_type == 'all':
                search_title = Book.objects.filter(title__icontains=i)
                search_author = Book.objects.filter(author__icontains=i)
                search_publisher = Book.objects.filter(publisher__icontains=i)
                search_subject = Book.objects.filter(book_subject__icontains=i)

                temp.extend(search_title.values_list('isbn10', flat=True))
                temp.extend(search_author.values_list('isbn10', flat=True))
                temp.extend(search_publisher.values_list('isbn10', flat=True))
                temp.extend(search_subject.values_list('isbn10', flat=True))

            elif query_type == 'author':
                search_author = Book.objects.filter(author__icontains=i)
                temp.extend(search_author.values_list('isbn10', flat=True))

            elif query_type == 'publisher':
                search_publisher = Book.objects.filter(publisher__icontains=i)
                temp.extend(search_publisher.values_list('isbn10', flat=True))

            elif query_type == 'category':
                search_category = Book.objects.filter(book_subject__icontains=i)
                temp.extend(search_category.values_list('isbn10', flat=True))

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
        book = Book.objects.get(isbn10=i)
        search_reviews = Review.objects.filter(isbn13=book.isbn13)
        temp_list = search_reviews.values_list('review_score', flat=True)

        if len(temp_list)!=0:
            average_score = sum(temp_list)*1.0/len(temp_list)
        else:
            average_score = 0
        append_this_dict = {'isbn10': i, 'isbn13': book.isbn13,'data': {  'hits': temp_dict[i][0],
                                                    'url': temp_dict[i][1],
                                                    'title': temp_dict[i][2].title,
                                                    'publisher': temp_dict[i][2].publisher,
                                                    'year': temp_dict[i][2].years,
                                                    'author': temp_dict[i][2].author,
                                                    'average_score': average_score}}
        isbn_list_of_dicts.append(append_this_dict)
    return isbn_list_of_dicts

def book_details(request, bid):
    book = get_object_or_404(Book, isbn10=bid)
    reviews = Review.objects.filter(isbn13=book.isbn13)
    username = request.user.username
    user = User.objects.get(username=username)
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


    return render(request, 'bookstore/book_details.html', {'book': book, 'book_img': book_img, 'avg_score': rounded_score, 'uscore':uscore, 'reviews':reviews})

@login_required
def review(request, bid):
    book = get_object_or_404(Book, isbn10=bid)
    #TODO: Check if user is currently logged in, if not redirect to login page

    #get username uname = ''
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
        return render(request, 'bookstore/book_details.html', {'book': book, 'book_img': book_img, 'avg_score':rounded_score, 'uscore':uscore, 'error_message':"Please enter a valid review!"})

    #if user has valid review, insert into Review table
    review = Review(login_name=user, isbn13=book, review_score=uscore, review_text=ureview, review_date=datetime.date.today())
    review.save()
    return render(request, 'bookstore/review_success.html', {'book':book})

@login_required
def add_to_cart(request, bid):
    book = get_object_or_404(Book, isbn10=bid)

    #TODO: Check if user is logged in, get user id
    username = request.user.username
    #Insert to shopping cart
    shopcart = ShoppingCart(login_name=User.objects.get(username=username), isbn13=book, num_order=1,order_date=datetime.date.today())
    shopcart.save()

    return render(request, 'bookstore/index.html', {'book_in_cart': book.title})


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
            if len(k)== 13:
                user = User.objects.get(username=username)
                book = Book.objects.get(isbn13=k)
                order_status = "Processed"
                order = CustomerOrder(login_name=user, isbn13=book, num_order=int(v), order_date=datetime.date.today()+datetime.timedelta(1), order_status=order_status)
                order.save()

                ShoppingCart.objects.filter(login_name=user).delete()

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
