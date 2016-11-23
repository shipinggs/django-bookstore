from django.contrib import admin

# Register your models here.
from .models import Customer, Book, Review, Orders, Rate, Shoppingcart

admin.site.register(Customer)
admin.site.register(Book)
admin.site.register(Review)
admin.site.register(Orders)
admin.site.register(Rate)
admin.site.register(Shoppingcart)
