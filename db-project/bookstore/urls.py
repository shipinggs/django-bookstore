from django.conf.urls import url

from . import views

app_name = 'bookstore'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^account$', views.AccountView.as_view(), name='account'),
    url(r'^admin$', views.BookstoreAdminView.as_view(), name='admin'),
    url(r'^cart$', views.CartView.as_view(), name='cart'),
    url(r'^home$', views.home, name='home'),
    url(r'^login$', views.LoginFormView.as_view(), name='login'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),
    url(r'^register$', views.RegistrationFormView.as_view(), name='register'),
    url(r'^book/(?P<bid>[a-zA-Z0-9]+)$', views.book_details, name = 'book_details'),
 	url(r'^book/(?P<bid>[a-zA-Z0-9]+)/add-to-cart$', views.add_to_cart, name = 'add_to_cart'),
 	url(r'^book/(?P<bid>[a-zA-Z0-9]+)/review', views.review, name = 'review'),
    url(r'^search/(?P<key>.*)$', views.search, name='search'),
    url(r'^search/(?P<key>.*)/filter-author$', views.search_filter_author, name='search_filter_author'),
]
