from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Review, ShoppingCart, CustomerOrder, Rate
from django.db.models import Q, Sum, Count, Avg
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

from .forms import SearchForm, UserRegistrationForm, ProfileForm, LoginForm, NewBookForm, AddCopiesForm, StatisticsForm

isbn_list_of_dicts = []

def home(request):
    #TODO: add functionality
    if request.user.is_authenticated():
        recommended = query(request.user.id, 'recommend')
        request.session['recommended'] = recommended
        request.session.modified = True

        # If there are no books bought yet or nothing to recommend
        if len(recommended) == 0:
            return render(request, 'bookstore/index.html', {'books': request.session['recommended'], 'flag': False})

        else:
            return render(request, 'bookstore/index.html', {'books': request.session['recommended'], 'flag': True})
    else:
        return render(request, 'bookstore/index.html', {'books': '', 'flag': False})


def search(request):
    """Book search based on authors, and/or publisher, and/or title, and/or subjec"""
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # print (request.GET['search_value'])
        isbn_list_of_dicts = []

        # check whether it's valid:
        if form.is_valid():
            temp_dict = {}

            # Gets the search values, which is determined by what the user has typed into search bar
            search_values = form.cleaned_data['search_value'].split(" ")
            search_values = list(filter(None, search_values))

            #print ("Search form")
            #print (search_values)


            # calls the query function to get list of dictionaries of book data
            isbn_list_of_dicts = query(search_values, 'all')

    # No such results could be found
    if len(isbn_list_of_dicts) == 0:
        return render(request, 'bookstore/search_results.html', {'books': request.session['isbn_list_of_dicts'], 'status': 'No results could be found :('})

    request.session['isbn_list_of_dicts'] = isbn_list_of_dicts
    request.session.modified = True
    return render(request, 'bookstore/search_results.html', {'books': request.session['isbn_list_of_dicts'] , 'status': 'Search results for "%s"'%(' '.join(search_values))})

# Filters the search results by author
def search_filter_author(request):
    return render(request, 'bookstore/search_filter_author.html', {'books': request.session['isbn_list_of_dicts']})

# Filters the search results by year
def search_filter_year(request):
    return render(request, 'bookstore/search_filter_year.html', {'books': request.session['isbn_list_of_dicts']})

# Filters the search results by review_score
def search_filter_score(request):
    return render(request, 'bookstore/search_filter_score.html', {'books': request.session['isbn_list_of_dicts']})

# Returns a search result based on click event: Either by a certain publisher, author or category
def search_specific(request, key, specified):
    # Gets the search values, which is determined by the click event and returns a list of dictionaries
    search_values = [specified]
    isbn_list_of_dicts = query(search_values, key)
    request.session['isbn_list_of_dicts'] = isbn_list_of_dicts
    request.session.modified = True
    return render(request, 'bookstore/search_results.html', {'books': request.session['isbn_list_of_dicts'], 'status': 'Search results for "%s" under %s'%(' '.join(search_values), key)})

def query(search_values, query_type):
    # Get isbn hit count from book table
    isbn_list_of_dicts = []
    temp_dict = {}

    # Case when the recommender system is deployed
    if query_type == 'recommend':
        temp = []
        # get all orders of the current user
        search_user_books = CustomerOrder.objects.filter(login_name=search_values)
        # get all the isbn13 of these orders
        current_user_books = []
        current_user_books.extend(search_user_books.values_list('isbn13', flat=True))
        other_users = []

        # Gets the user id of the users who have ordered books that the user has ordered before
        for i in current_user_books:
            temp_users = CustomerOrder.objects.filter(isbn13=i)
            other_users.extend(temp_users.values_list('login_name', flat=True))

        # Removes the user's user id so that it will purely recommend new books
        other_users = list(set(other_users))
        if search_values in other_users:
            other_users.remove(search_values)

        # Gets the list of isbn13 that other users with similar taste have ordered
        temp_isbn13 = []
        for i in other_users:
            temp_other_user_books = CustomerOrder.objects.filter(login_name=i)
            temp_isbn13.extend(temp_other_user_books.values_list('isbn13', flat=True))

        # Gets the isbn10 of the books and removes the books that the user has ordered before
        for i in temp_isbn13:
            if i not in current_user_books:
                book = Book.objects.get(isbn13=i)
                temp.append(book.isbn10)

    else:
        for i in search_values:
            temp = []

            # Case when the user types into the search bar and searches
            if query_type == 'all':
                if ' '.join(search_values).count(';') != 3:
                    # Conjunctive search
                    # Gets the list of books' isbn10 that contain keywords from search bar
                    search_title = Book.objects.filter(title__icontains=i)
                    search_author = Book.objects.filter(author__icontains='')
                    search_publisher = Book.objects.filter(publisher__icontains=i)
                    search_subject = Book.objects.filter(book_subject__icontains=i)

                    temp.extend(search_title.values_list('isbn10', flat=True))
                    temp.extend(search_author.values_list('isbn10', flat=True))
                    temp.extend(search_publisher.values_list('isbn10', flat=True))
                    temp.extend(search_subject.values_list('isbn10', flat=True))

                    # Separated search
                    # Combines the list from the search back into the original sentence and split at commas instead
                    # index in final form refers to the following
                    # [title, author, publisher, category]
                else:
                    new_search_values = ' '.join(search_values).split(';')
                    search_dict = {'title':new_search_values[0],'author':new_search_values[1],'publisher':new_search_values[2],'subject':new_search_values[3]}
                    search_title = Q(title__icontains=new_search_values[0])
                    search_author = Q(author__icontains=new_search_values[1])
                    search_publisher = Q(publisher__icontains=new_search_values[2])
                    search_subject = Q(book_subject__icontains=new_search_values[3])

                    reference_list = {'title':search_title,'author':search_author,'publisher':search_publisher,'subject':search_subject}
                    queries = [search_title,search_author,search_publisher,search_subject]
                    # removes those fields with no user input
                    for i in search_dict:
                        if len(search_dict[i]) == 0:
                            queries.remove(reference_list[i])

                    print (queries)
                    if len(queries) == 0:
                        break

                    queries_and = ""

                    if len(queries) == 1:
                        queries_and = queries[0]
                        search_results = Book.objects.filter(queries_and)
                        temp.extend(search_results.values_list('isbn10', flat=True))

                    # if thhe queries len more than
                    elif len(queries) > 1:
                        queries_and = queries[0]
                    # AND the Q object with the ones remaining in the list
                        for item in queries[1:]:
                            queries_and &= item
                        search_results = Book.objects.filter(queries_and)
                        temp.extend(search_results.values_list('isbn10', flat=True))

                    print (queries_and)
                    break

            # Case when the user clicks an author
            elif query_type == 'author':
                # Gets the list of books' isbn10 written by a certain author
                search_author = Book.objects.filter(author__icontains=i)
                temp.extend(search_author.values_list('isbn10', flat=True))

            # Case when the user clicks a publisher
            elif query_type == 'publisher':
                # Gets the list of books' isbn10 published by a certain publisher
                search_publisher = Book.objects.filter(publisher__icontains=i)
                temp.extend(search_publisher.values_list('isbn10', flat=True))

            # Case when the user clicks a category
            elif query_type == 'category':
                # Gets the list of books' isbn10 from a certain category
                search_category_1 = Book.objects.filter(book_subject__icontains=i)
                search_category_2 = Book.objects.filter(keyword__icontains=i)
                temp.extend(search_category_1.values_list('isbn10', flat=True))
                temp.extend(search_category_2.values_list('isbn10', flat=True))

    # Iterates through the list of books' isbn10 and counts the number of times the isbn10 appears in list
    for j in temp:
        if j in temp_dict:
            temp_dict[j][0] += 1
        else:
            temp_dict[j] = [1]
    # Gets the book images to be used in the html page, appends it to temp_dict
    for i in temp_dict:
        uri = "http://www.goodreads.com/book/title?format=xml&key=VZTtD5ycbJ7Azy1BnZmg&isbn=%s"%(str(i))
        try:
            f = urllib.request.urlopen(uri)
            data = f.read()
            f.close()

            data = xmltodict.parse(data)
            # print (data['GoodreadsResponse']['book']['image_url'])
            book_img = data['GoodreadsResponse']['book']['image_url']
        except:
            # print ('excepted yo')
            book_img = 'http://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png'
        finally:
            temp_dict[i].append(book_img)

    # Gets the book object from the isbn10
    for i in temp_dict:
        temp_dict[i].append(get_object_or_404(Book, isbn10=i))

    # Gets the required details from the books and puts them into a dictionary for reference in html page
    for i in temp_dict:
        # Gets the reviews of a certain book
        book = Book.objects.get(isbn10=i)
        search_reviews = Review.objects.filter(isbn13=book.isbn13)

        # Averages the review score over the number of reviews
        temp_list = search_reviews.values_list('review_score', flat=True)
        if len(temp_list)!=0:
            average_score = sum(temp_list)*1.0/len(temp_list)
        else:
            average_score = 0

        # This dictionary will be appended to a list which will then be used in the html page
        append_this_dict = {
            'isbn10': i,
            'isbn13': book.isbn13,
            'data': {
                'hits': temp_dict[i][0],
                'url': temp_dict[i][1],
                'title': temp_dict[i][2].title,
                'publisher': temp_dict[i][2].publisher,
                'year': temp_dict[i][2].years,
                'author': temp_dict[i][2].author,
                'average_score': average_score
            }
        }
        isbn_list_of_dicts.append(append_this_dict)
    return isbn_list_of_dicts

def book_details(request, bid, sort_newest=True, rnum=None):
    book = get_object_or_404(Book, isbn10=bid)
    reviews= Review.objects.filter(isbn13=book).order_by('review_date').reverse()
    num_reviews = 5
    if "num_review" in request.POST:
        num_reviews = int(request.POST.get('num_review'))
    elif rnum:
        num_reviews = int(rnum)

    reviews = reviews[:num_reviews]
    #get total rating for each review
    r = Rate.objects.filter(isbn13=book).values('rated').annotate(Avg('rating'))

    #get list of reviews for book, order by newest
    no_reviews = len(reviews)
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
                item = {'login_name': review.login_name,
                            'id': review.id,
                            'review_score': review.review_score,
                            'review_text': review.review_text,
                            'review_date': review.review_date,
                            'total_rating': 0,
                    }
                if review.id == rate['rated']:
                    item = {'login_name': review.login_name,
                            'id': review.id,
                            'review_score': review.review_score,
                            'review_text': review.review_text,
                            'review_date': review.review_date,
                            'total_rating': rate['rating__avg'],
                    }
                review_list_best.append(item)
        reviews = sorted(review_list_best, key=itemgetter('total_rating'), reverse=True)[:num_reviews]

    return render(request, 'bookstore/book_details.html', {'book': book, 'book_img': book_img, 'avg_score': rounded_score, 'uscore':uscore, 'reviews':reviews, 'review_ratings':r, "no_reviews":no_reviews, 'rnum':num_reviews, 'sort_newest': sort_newest} )

def review_filter_newest(request, bid, rnum):
    rend = book_details(request, bid, rnum=rnum)
    return rend

def review_filter_best(request, bid, rnum):
    rend = book_details(request, bid, sort_newest=False, rnum=rnum)
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
            raise Exception("Error")
        rate = Rate(rater=user,rated=review,rating=int(rating),isbn13=book)
        rate.save()
    except IntegrityError as ie:
        messages.add_message(request, messages.WARNING, "You have already rated this review!")
        return HttpResponseRedirect(reverse('bookstore:book_details', args=(bid,)))
    except Exception as e:
        messages.add_message(request, messages.WARNING, "You cannot rate your own review.")
        return HttpResponseRedirect(reverse('bookstore:book_details', args=(bid,)))

    return HttpResponseRedirect(reverse("bookstore:book_details", args=(bid,)))


class AccountView(View):
    template_name = 'bookstore/account.html'

    def get(self, request):
        user = request.user
        orders = CustomerOrder.objects.filter(login_name=user.id)
        books_ordered = Book.objects.filter(isbn13__in=orders.values('isbn13'))
        orders_with_details = []
        for order in orders:
            for book in books_ordered:
                if order.isbn13.isbn13 == book.isbn13:
                    orders_with_details.append({
                        'date': order.order_date,
                        'title': book.title,
                        'isbn10': book.isbn10,
                        'isbn13': book.isbn13,
                        'price': book.price,
                        'quantity': order.num_order,
                        'total_cost': book.price * order.num_order
                    })

        reviews = Review.objects.filter(login_name=user.id)
        books_reviewed = Book.objects.filter(isbn13__in=reviews.values('isbn13'))
        reviews_with_details = []
        for review in reviews:
            for book in books_reviewed:
                if review.isbn13.isbn13 == book.isbn13:
                    reviews_with_details.append({
                        'title': book.title,
                        'isbn10': book.isbn10,
                        'isbn13': book.isbn13,
                        'date': review.review_date,
                        'score': review.review_score,
                        'text': review.review_text
                    })

        ratings = Rate.objects.filter(rater=user.id).order_by('-rating')
        books_rated = Book.objects.filter(isbn13__in=ratings.values('isbn13'))
        ratings_with_details = []
        for rate in ratings:
            for book in books_rated:
                if rate.isbn13.isbn13 == book.isbn13:
                    rating_string = ''
                    if (rate.rating == 0):
                        rating_string = 'Useless'
                    elif (rate.rating == 1):
                        rating_string = 'Useful'
                    else:
                        rating_string = 'Very useful'

                    ratings_with_details.append({
                        'title': book.title,
                        'isbn10': book.isbn10,
                        'isbn13': book.isbn13,
                        'reviewer': rate.rated.login_name.first_name + ' ' + rate.rated.login_name.last_name,
                        'review_score': rate.rated.review_score,
                        'review_text': rate.rated.review_text,
                        'rating': rating_string
                    })

        return render(request, self.template_name, {
            'orders': orders_with_details,
            'reviews': reviews_with_details,
            'ratings': ratings_with_details
        })

class BookstoreAdminView(UserPassesTestMixin, View):
    raise_exception = True
    new_book_form_class = NewBookForm
    add_copies_form_class = AddCopiesForm
    template_name = 'bookstore/bookstore-admin.html'

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        new_book_form = self.new_book_form_class(None)
        add_copies_form = self.add_copies_form_class(None)
        return render(request, self.template_name, {
            'new_book_form': new_book_form,
            'add_copies_form': add_copies_form
        })

    def post(self,request):
        new_book_form = self.new_book_form_class(request.POST)
        add_copies_form = self.add_copies_form_class(request.POST)
        message = ''
        print (request.POST)
        if ('new-book-submit' in request.POST) and new_book_form.is_valid():
            add_copies_form = self.add_copies_form_class(None)
            new_book_form.save()
            message = 'Book has been successfully added.'

        elif ('add-copies-submit' in request.POST) and add_copies_form.is_valid():
            new_book_form = self.new_book_form_class(None)
            isbn13 = request.POST['isbn13']
            num_copies_added = int(request.POST['num_copies'])

            try:
                book = Book.objects.get(isbn13=isbn13)
                book.num_copies += num_copies_added
                book.save()
                message = 'Copies are successfully added.'

            except:
                message = 'Book with ISBN13 ' + isbn13 + ' not found'

        return render(request, self.template_name, {
            'new_book_form': new_book_form,
            'add_copies_form': add_copies_form,
            'message': message
        })

class CartView(View):
    template_name = 'bookstore/cart.html'

    def get(self, request, not_enough=[]):
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
        if len(not_enough) > 0:
            content['not_enough'] = not_enough

        return render(request, self.template_name, content)

class OrderView(View):

    def post(self, request):
        username = request.user.username
        insufficient_stock = []
        for k,v in request.POST.items():
            if "Submit" in request.POST.keys():
                if len(k)== 13:
                    user = User.objects.get(username=username)
                    book = Book.objects.get(isbn13=k)
                    if book.num_copies - int(v) < 0:
                        insufficient_stock.append(book.isbn13)
                    else:
                        book.num_copies = book.num_copies - int(v)
                        book.save()
                        order_status = "Processed"
                        order = CustomerOrder(login_name=user, isbn13=book, num_order=int(v), order_date=datetime.date.today()+datetime.timedelta(1), order_status=order_status)
                        order.save()

                        book.num_copies -= int(v)
                        if book.num_copies < 0:
                            book.num_copies = 0
                        book.save()

                        ShoppingCart.objects.get(login_name=user, isbn13=book).delete()
            else:
                user = User.objects.get(username=username)
                ShoppingCart.objects.filter(login_name=user, isbn13=request.POST['remove']).delete()
        if len(insufficient_stock) > 0:
            return CartView().get(self.request, not_enough=insufficient_stock)

        return HttpResponseRedirect(reverse('bookstore:cart'))

    def get(self, request):
        return HttpResponseRedirect(reverse('bookstore:cart'))

class StatisticsView(UserPassesTestMixin, View):
    raise_exception = True
    statistics_form_class = StatisticsForm
    template_name = 'bookstore/statistics.html'

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        statistics_form = self.statistics_form_class(None)
        return render(request, self.template_name, {
            'form': statistics_form
        })

    def post(self, request):
        statistics_form = self.statistics_form_class(request.POST)
        if statistics_form.is_valid():
            month = request.POST['month']
            view_top = int(request.POST['view_top'])
            orders = CustomerOrder.objects.filter(order_date__month=month)
            books = []
            authors = []
            publishers = []
            book_count = {}
            author_count = {}
            publisher_count = {}
            for order in orders:
                if order.isbn13.isbn13 not in book_count:
                    book_count[order.isbn13.isbn13] = order.num_order
                else:
                    book_count[order.isbn13.isbn13] += order.num_order

                if order.isbn13.author not in author_count:
                    author_count[order.isbn13.author] = order.num_order
                else:
                    author_count[order.isbn13.author] += order.num_order

                if order.isbn13.publisher not in publisher_count:
                    publisher_count[order.isbn13.publisher] = order.num_order
                else:
                    publisher_count[order.isbn13.publisher] += order.num_order

            # sort books by number of orders
            sorted_book_count = sorted(book_count.items(), key=itemgetter(1), reverse=True)[:view_top]
            sorted_author_count = sorted(author_count.items(), key=itemgetter(1), reverse=True)[:view_top]
            sorted_publisher_count = sorted(publisher_count.items(), key=itemgetter(1), reverse=True)[:view_top]


            for (isbn13, count) in sorted_book_count:
                book = Book.objects.get(isbn13=isbn13)
                books.append({
                    'title': book.title,
                    'author': book.author,
                    'isbn10': book.isbn10,
                    'isbn13': book.isbn13,
                    'copies_sold': count
                })


        return render(request, self.template_name, {
            'form': statistics_form,
            'request_post': True,
            'books': books,
            'authors': sorted_author_count,
            'publishers': sorted_publisher_count
        })


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
            if ('logout' in self.request.GET.get('next')):
                return redirect('bookstore:home')
            return redirect(self.request.GET.get('next', 'bookstore:home'))

        return render(request, self.template_name, {
            'form': form,
            'error_message': 'The username and password provided do not match'
        })
