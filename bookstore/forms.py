from django import forms
from .models import Book, Category
from django import forms
from .models import SellerProfile  
from .models import Review

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


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'price', 'category', 'description', 'stock', 'image']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_text', 'image']  
