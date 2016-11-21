from django.http import HttpResponse
from django.shortcuts import render

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
