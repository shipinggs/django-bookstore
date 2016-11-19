from django.contrib import admin

# Register your models here.
from .models import Customers, Books, Feedbacks, Orders, Rates

admin.site.register(Customers)
admin.site.register(Books)
admin.site.register(Feedbacks)
admin.site.register(Orders)
admin.site.register(Rates)
