from django.db import models

# Create your models here.
class Books(models.Model):
    isbn13 = models.CharField(max_length=14, min_length=14, primary_key=True)
    isbn10 = models.CharField(max_length=10, min_length=10, unique=True)
    title = models.CharField(max_length=256, null=False)
    author = models.CharField(max_length=256)
    year = models.IntegerField(default=0)
    num_copies = models.IntegerField(min_length=1)
