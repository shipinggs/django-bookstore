from django.contrib import admin

# Register your models here.
from .models import Customer, Book, Review, CustomerOrder, Rate, ShoppingCart

admin.site.register(Customer)
admin.site.register(Book)
admin.site.register(Review)
admin.site.register(CustomerOrder)
admin.site.register(Rate)
admin.site.register(ShoppingCart)
