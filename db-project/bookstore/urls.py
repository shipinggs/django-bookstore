from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^account$', views.account, name='account'),
    url(r'^admin$', views.admin, name='admin'),
    url(r'^cart$', views.cart, name='cart'),
    url(r'^home$', views.home, name='home'),
    url(r'^login$', views.login, name='login'),
    # url(r'^$', views.index, name='index'),
    url(r'^query$', views.query, name='query'),
    url(r'^register$', views.register, name='register'),
    url(r'^book/(?P<bid>[a-zA-Z0-9]+)$', views.book_details, name = 'book_details'),
 	url(r'^book/(?P<bid>[a-zA-Z0-9]+)/add-to-cart$', views.add_to_cart, name = 'add_to_cart'),
 	url(r'^book/(?P<bid>[a-zA-Z0-9]+)/review$', views.review, name = 'review'),
    url(r'^search$', views.search, name='search'),

]

