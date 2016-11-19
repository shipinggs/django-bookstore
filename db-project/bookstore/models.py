# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Books(models.Model):
    isbn13 = models.CharField(db_column='ISBN13', primary_key=True, max_length=14)  # Field name made lowercase.
    isbn10 = models.CharField(db_column='ISBN10', unique=True, max_length=10)  # Field name made lowercase.
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    num_copies = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    book_format = models.CharField(max_length=9, blank=True, null=True)
    keyword = models.CharField(max_length=255, blank=True, null=True)
    book_subject = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'books'


class Customers(models.Model):
    login_name = models.CharField(primary_key=True, max_length=255)
    fullname = models.CharField(max_length=255, blank=True, null=True)
    login_password = models.CharField(max_length=255)
    credit_card = models.CharField(max_length=16, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customers'


class Feedbacks(models.Model):
    login_name = models.ForeignKey(Customers, models.DO_NOTHING, db_column='login_name')
    isbn13 = models.ForeignKey(Books, models.DO_NOTHING, db_column='ISBN13')  # Field name made lowercase.
    feedback_score = models.IntegerField(blank=True, null=True)
    feedback_text = models.CharField(max_length=255, blank=True, null=True)
    feedback_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feedbacks'
        unique_together = (('login_name', 'isbn13'),)


class Orders(models.Model):
    login_name = models.ForeignKey(Customers, models.DO_NOTHING, db_column='login_name')
    isbn13 = models.ForeignKey(Books, models.DO_NOTHING, db_column='ISBN13')  # Field name made lowercase.
    num_order = models.IntegerField(blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    order_status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders'
        unique_together = (('login_name', 'isbn13'),)


class Rates(models.Model):
    rater = models.ForeignKey(Customers, models.DO_NOTHING, db_column='rater', related_name='rater_content_type')
    rated = models.ForeignKey(Customers, models.DO_NOTHING, db_column='rated', related_name='rated_content_type')
    rating = models.IntegerField()
    isbn13 = models.ForeignKey(Books, models.DO_NOTHING, db_column='ISBN13')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rates'
        unique_together = (('rater', 'rated', 'isbn13'),)
