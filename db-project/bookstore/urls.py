from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'account', views.account, name='account'),
    url(r'admin', views.admin, name='admin'),
    url(r'cart', views.cart, name='cart'),
    url(r'home', views.home, name='home'),
    url(r'login', views.login, name='login'),
    # url(r'^$', views.index, name='index'),
    url(r'query', views.queryer, name='query'),
    url(r'register', views.register, name='register'),
]
