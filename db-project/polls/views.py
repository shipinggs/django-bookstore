from django.http import HttpResponse

def index(request):
    return HttpResponse('<h1>Polls App</h1>')
