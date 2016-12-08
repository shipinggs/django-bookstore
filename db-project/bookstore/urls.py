from django.conf.urls import url

from . import views

app_name = 'bookstore'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^account$', views.AccountView.as_view(), name='account'),
    url(r'^admin$', views.BookstoreAdminView.as_view(), name='admin'),
    url(r'^stats$', views.StatisticsView.as_view(), name='stats'),
    url(r'^cart$', views.CartView.as_view(), name='cart'),
    url(r'^cart/order', views.OrderView.as_view(), name='order'),
    url(r'^home$', views.home, name='home'),
    url(r'^login$', views.LoginFormView.as_view(), name='login'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),
    url(r'^register$', views.RegistrationFormView.as_view(), name='register'),
    url(r'^book/(?P<bid>[a-zA-Z0-9]+)/review-filter-newest/(?P<rnum>[0-9]+)', views.review_filter_newest, name = 'review_filter_newest'),
    url(r'^book/(?P<bid>[a-zA-Z0-9]+)/review-filter-best/(?P<rnum>[0-9]+)', views.review_filter_best, name = 'review_filter_best'),
 	url(r'^book/(?P<bid>[a-zA-Z0-9]+)/add-to-cart$', views.add_to_cart, name = 'add_to_cart'),
 	url(r'^book/(?P<bid>[a-zA-Z0-9]+)/review$', views.review, name = 'review'),
    url(r'^book/(?P<bid>[a-zA-Z0-9]+)/review/rate/(?P<rid>[0-9]+)$', views.rate_user_review, name = 'rate_user_review'),
    
    url(r'^book/(?P<bid>[a-zA-Z0-9]+)', views.book_details, name = 'book_details'),
    url(r'^search/$', views.search, name='search'),
    url(r'^search/filter-author$', views.search_filter_author, name='search_filter_author'),
    url(r'^search/filter-year$', views.search_filter_year, name='search_filter_year'),
    url(r'^search/filter-score$', views.search_filter_score, name='search_filter_score'),
    url(r'^keyword/(?P<key>[a-zA-Z0-9]+)/(?P<specified>.*)$', views.search_specific, name='search_specific'),
]
