from django import forms
from .models import Book, Category
from django import forms
from .models import SellerProfile  

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'price', 'category', 'description', 'image']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class SellerSignupForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['store_name', 'phone_number', 'address']
