# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Book(models.Model):
    isbn13 = models.CharField(db_column='ISBN13', primary_key=True, max_length=14)  # Field name made lowercase.
    isbn10 = models.CharField(db_column='ISBN10', unique=True, max_length=10)  # Field name made lowercase.
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    years = models.IntegerField()
    num_copies = models.IntegerField()
    price = models.FloatField()
    format_choices = (('Hardcover', 'Hardcover'), ('Paperback', 'Paperback'))
    book_format = models.CharField(max_length=9, choices=format_choices)
    keyword = models.CharField(max_length=255, blank=True, null=True)
    book_subject = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'book'

class CustomerOrder(models.Model):
    login_name = models.ForeignKey(User, models.DO_NOTHING, db_column='login_name')
    isbn13 = models.ForeignKey(Book, models.DO_NOTHING, db_column='ISBN13')  # Field name made lowercase.
    num_order = models.IntegerField(blank=True, null=True)
    order_date = models.DateField()
    order_status = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'customer_order'



class Rate(models.Model):
    rater = models.ForeignKey(User, models.DO_NOTHING, db_column='rater', related_name='%(class)s_rater_requests_created')
    rated = models.ForeignKey('Review', models.DO_NOTHING, db_column='rated', related_name='%(class)s_rated_requests_created')
    rating = models.IntegerField()
    isbn13 = models.ForeignKey(Book, models.DO_NOTHING, db_column='ISBN13', related_name='%(class)s_isbn13_requests_created')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'rate'
        unique_together = (('rater', 'rated', 'isbn13'),)


class Review(models.Model):
    login_name = models.ForeignKey(User, models.DO_NOTHING, db_column='login_name')
    isbn13 = models.ForeignKey(Book, models.DO_NOTHING, db_column='ISBN13')  # Field name made lowercase.
    review_score = models.IntegerField(blank=True, null=True)
    review_text = models.CharField(max_length=255, blank=True, null=True)
    review_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'review'
        unique_together = (('login_name', 'isbn13'),)


class ShoppingCart(models.Model):
    login_name = models.ForeignKey(User, models.DO_NOTHING, db_column='login_name')
    isbn13 = models.ForeignKey(Book, models.DO_NOTHING, db_column='ISBN13')  # Field name made lowercase.
    num_order = models.IntegerField(blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'shopping_cart'
        unique_together = (('login_name', 'isbn13'),)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credit_card_number = models.CharField(max_length=16, default='')
    mailing_address = models.TextField(max_length=255, default='')
    phone_number = models.CharField(max_length=50, default='')

    class Meta:
        managed = True
        db_table = 'user_profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    if created:
        instance.profile.save()
