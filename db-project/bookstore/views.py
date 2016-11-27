from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Review
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

def home(request):
    #TODO: add functionality
    return render(request, 'bookstore/index.html')


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

def book_details(request, bid):
    book = get_object_or_404(Book, isbn10=bid)
    reviews = Review.objects.filter(isbn13=book.isbn13)
    avg_score = 0
    if reviews:
        for review in reviews:
            avg_score += review.review_score
        avg_score = avg_score/len(reviews)

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

    uscore = 5
    return render(request, 'bookstore/book_details.html', {'book': book, 'book_img': book_img, 'avg_score': avg_score, 'uscore':uscore})

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
        return render(request, 'bookstore/book_details.html', {'book': book, 'book_img': book_img, 'avg_score':avg_score, 'uscore':uscore, 'error_message':"Please enter a valid review!"})

    #if user has valid review, insert into Review table
    review = Review(login_name=user, isbn13=book, review_score=uscore, review_text=ureview, review_date=datetime.date.today())
    review.save()
    return render(request, 'bookstore/review_success.html', {'book':book})

@login_required
def add_to_cart(request, bid):
    book = get_object_or_404(Book, isbn10=bid)

    #TODO: Check if user is logged in, get user id
    user_id = request.user.id
    print (user_id)
    #Insert to shopping cart
    #shopcart = ShoppingCart(login_name=, isbn13=book.isbn13, num_order=1,order_date=datetime.date)
    #shopcart.save()
    return HttpResponseRedirect(reverse('bookstore:home'))


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
        return render(request, self.template_name)


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
