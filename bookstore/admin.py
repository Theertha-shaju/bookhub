from django.contrib import admin
from .models import Book  # Import only Book model

# Register your models here.
admin.site.register(Book)
