from django.db import models  
from django.contrib.auth.models import User  
from django.utils.text import slugify  
from django.core.validators import MinLengthValidator, MaxLengthValidator  
from django.shortcuts import render


# ✅ Helper Function: Unique Slug Generation  
def generate_unique_slug(instance, model, field_name="title"):
    """Generate a unique slug for a given model instance."""
    base_slug = slugify(getattr(instance, field_name))
    slug = base_slug
    count = 1
    while model.objects.exclude(pk=instance.pk).filter(slug=slug).exists():
        slug = f"{base_slug}-{count}"
        count += 1
    return slug

# ✅ Seller Profile Model  
class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    store_name = models.CharField(max_length=255, unique=True, verbose_name="Store Name")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Phone Number")
    address = models.TextField(blank=True, null=True, verbose_name="Address")

    def __str__(self):
        return self.store_name

    class Meta:
        db_table = "bookstore_sellerprofile"
        verbose_name_plural = "Sellers"

# ✅ Category Model  
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, db_index=True)  

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, Category, "name")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name  

    class Meta:
        verbose_name_plural = "Categories"

# ✅ Book Model  
class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Book Title")
    slug = models.SlugField(unique=True, blank=True, db_index=True)  
    author = models.CharField(max_length=255, verbose_name="Author Name")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price (₹)")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="books", verbose_name="Category", db_index=True)
    image = models.ImageField(upload_to='book_images/', verbose_name="Book Cover Image")
    description = models.TextField(blank=True, null=True, verbose_name="Book Description")
    stock = models.PositiveIntegerField(default=10, verbose_name="Stock Available")
    published_date = models.DateField(blank=True, null=True, verbose_name="Publication Date")
    rating = models.FloatField(default=0) 
    isbn = models.CharField(
        max_length=13, unique=True, blank=True, null=True, verbose_name="ISBN (Unique)",
        validators=[MinLengthValidator(13), MaxLengthValidator(13)]
    )
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Seller", related_name="books")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, Book)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/book/{self.slug}/"

    def __str__(self):
        return f"{self.title} by {self.author}"  

    class Meta:
        verbose_name_plural = "Books"

# ✅ Review Model  
class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews", verbose_name="Book")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    review_text = models.TextField(verbose_name="Review Text")
    image = models.ImageField(upload_to='review_images/', blank=True, null=True, verbose_name="Review Image")
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(null=True, blank=True, default=0)


    def __str__(self):
        return f"Review by {self.user.username} on {self.book.title} ({self.created_at:%Y-%m-%d})"  

    class Meta:
        verbose_name_plural = "Reviews"

# ✅ Cart Model  
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items", db_index=True)  
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="cart_entries", db_index=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bookstore_cart"  
        verbose_name_plural = "Cart Items"
        unique_together = ('user', 'book')  

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.quantity})"  

    @property
    def total_price(self):
        """Calculate total price for this cart entry."""
        return self.book.price * self.quantity
 # if in same app or import properly

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=20, unique=True)  # E.g., BH01, BH02, etc.
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    ordered_at = models.DateTimeField(auto_now_add=True)
    shipping_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Unpaid')
    billing_address = models.TextField(null=True, blank=True)  # Can also be City/State for privacy
    delivery_method = models.CharField(max_length=100, null=True, blank=True)  # Optional field

    def __str__(self):
        return self.order_id

# ✅ OrderItem Model (Move this below Order)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.book.title} - {self.quantity}"
    
    def subtotal(self):
        return self.price * self.quantity  # Calculate subtotal for this item

# ✅ Payment Model  
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("Razorpay", "Razorpay"),
        ("COD", "Cash on Delivery"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Success", "Success"),
        ("Failed", "Failed"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment", db_index=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default="Razorpay")
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.TextField(blank=True, null=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default="Pending", db_index=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bookstore_payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.payment_method} ({self.payment_status})"
  
class Buyer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Seller(models.Model,):
    name = models.CharField(max_length=255,null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class BookRating(models.Model):
    book = models.ForeignKey(Book, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # Ratings from 1 to 5
    review = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating for {self.book.title} by {self.user.username}"
    


def payment_details(request):
    # Fetch all payment details
    payments = Payment.objects.all()

    # Pass payments to the template
    return render(request, 'payment_details.html', {'payments': payments})
