from django.shortcuts import render, get_object_or_404, redirect,HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.urls import reverse 
from django.db.models import Sum
from django.contrib import messages
from django.db import transaction
from .models import Order, Cart
from .models import Book, Category, Cart, Order, Payment
from .forms import BookForm
from .models import Book
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from .models import Order, Book, Buyer 
from .models import Seller, Book, Order
from datetime import datetime, timedelta
from django.db.models import Sum, Count
from .models import Book, OrderItem, Order
from .models import Book, Order, Seller
from django.db.models import Avg, Count
from django.db.models.functions import TruncMonth
from .models import Book, Order
from django.utils import timezone
from datetime import timedelta
from .models import Order,Review,Buyer
# Ensure Buyer is imported


from django.contrib import messages



from .models import SellerProfile


from django.db.models.signals import post_save
from django.dispatch import receiver





 # ✅ Import reverse

from decimal import Decimal
from .models import Book, Category, Cart, Order  
from .models import Order, Payment  # ✅ Ensure Payment is imported

# import razorpay

from django.views.decorators.csrf import csrf_exempt
import logging
logger = logging.getLogger(__name__)


from django.conf import settings
import razorpay



razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))



# ✅ Home Page
def home(request):  
    return render(request, 'bookstore/home.html')

# ✅ Category View
def category_view(request):
    books = Book.objects.exclude(price__isnull=True, price=0)
    return render(request, 'bookstore/categories.html', {'books': books})

# ✅ Books by Category
def category_books(request, category_name):
    category = get_object_or_404(Category, name__iexact=category_name)
    books = Book.objects.filter(category=category).exclude(price__isnull=True, price=0)
    return render(request, 'bookstore/category_books.html', {'category_name': category_name, 'books': books})

# ✅ Book Detail View
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'bookstore/book_detail.html', {'book': book})


# ✅ Fiction Books View
def fiction_books(request):
    category = get_object_or_404(Category, name__iexact="Fiction")
    books = Book.objects.filter(category=category)
    return render(request, 'bookstore/fiction_books.html', {'books': books, 'category_name': "Fiction"})




# ✅ Non-Fiction Books View
def non_fiction_books(request):
    category = get_object_or_404(Category, name__iexact="Non-Fiction")
    books = Book.objects.filter(category=category)
    return render(request, 'bookstore/non_fiction_books.html', {'books': books, 'category_name': "Non-Fiction"})


# ✅ Science Fiction Books View
def science_fiction_books(request):
    category = get_object_or_404(Category, name__iexact='Science Fiction')
    books = Book.objects.filter(category=category)
    return render(request, 'bookstore/science_fiction_books.html', {'books': books})



def search_books(request):
    query = request.GET.get('query', '').strip()  # Get the search query

    if query:
        books = Book.objects.filter(title__icontains=query).values('id', 'title')  # Fetch matching books
        return JsonResponse({"books": list(books)})

    return JsonResponse({"books": []})  # Return empty list if no query
# ✅ User Login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        email_or_phone = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email_or_phone, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid email/phone or password.")
    return render(request, 'bookstore/login.html')

# ✅ User Signup

def signup_view(request):
    if request.method == "POST":
        email_or_phone = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        print(f"📌 Received: {email_or_phone}, {password}, {confirm_password}")  # Debugging

        if not email_or_phone:
            messages.error(request, "Email or Phone is required.")
            return redirect("signup")

        if not password or not confirm_password:
            messages.error(request, "Password fields cannot be empty.")
            return redirect("signup")

        try:
            validate_email(email_or_phone)
            is_email = True
        except ValidationError:
            is_email = False

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect("signup")

        if User.objects.filter(username=email_or_phone).exists():
            messages.error(request, "User already exists. Try logging in.")
            return redirect("signup")

        # ✅ Create and save user
        user = User.objects.create_user(
            username=email_or_phone,
            email=email_or_phone if is_email else "",
            password=password
        )
        user.save()
        print(f"✅ User Created: {user}")  # Debugging

        # ✅ Authenticate and login user
        user = authenticate(request, username=email_or_phone, password=password)
        if user:
            login(request, user)
            print(f"🎉 User Logged In: {user}")  # Debugging
            messages.success(request, f"Welcome, {user.username}! Signup successful.")
            return redirect("home")
        else:
            messages.error(request, "Something went wrong. Please try again.")
            return redirect("signup")

    return render(request, "bookstore/signup.html")  # Stay on signup page if errors


def admin_logout(request):
    logout(request)
    return redirect('admin_login') 
def admin_dashboard(request):
    # 📚 Total Books Sold
    total_books_sold = OrderItem.objects.aggregate(total_sold=Sum('quantity'))['total_sold'] or 0

    # 👥 Total Buyers Count
    total_buyers = Buyer.objects.count()

    # 💰 Total Payments Received
    total_payments = Order.objects.aggregate(total_amount=Sum('total_price'))['total_amount'] or 0

    # 📊 Top-Selling Books
    top_selling_books = OrderItem.objects.values('book__title').annotate(sold=Sum('quantity')).order_by('-sold')[:5]

    context = {
        'total_books_sold': total_books_sold,
        'total_buyers': total_buyers,
        'total_payments': total_payments,
        'top_selling_books': top_selling_books,
    }
    return render(request, 'bookstore/admin_dashboard.html')

def get_admin_data(request):
    data = {
        "total_sellers": SellerProfile.objects.count(),
        "total_books": Book.objects.count(),
        "total_orders": Order.objects.count(),
    }
    return JsonResponse(data)


def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid admin credentials.")
    return render(request, 'bookstore/admin_login.html')


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if not book.price or book.price <= 0:
        return HttpResponse("This book cannot be purchased.", status=400)
    cart_item, created = Cart.objects.get_or_create(user=request.user, book=book)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_view')

# ✅ Remove Book from Cart
@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect('cart_view')

# ✅ Update Cart Quantity
@login_required
def update_cart(request, cart_id, action):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    if action == "increase":
        cart_item.quantity += 1
        cart_item.save()
    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    else:
        return JsonResponse({"error": "Invalid action provided."}, status=400)
    return JsonResponse({"total_price": f"{cart_item.book.price * cart_item.quantity:.2f}"})

# ✅ View Cart Page
@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.book.price * item.quantity for item in cart_items)
    return render(request, 'bookstore/cart.html', {'cart_items': cart_items, 'total_price': total_price})



@login_required
def process_payment(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items.exists():
        return redirect("cart_view")  # Redirect if cart is empty
    
    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        if payment_method not in ["razorpay", "cod"]:
            messages.error(request, "Invalid payment method selected.")
            return redirect("cart_view")

        if payment_method == "razorpay":
            return redirect("razorpay_payment")  # Redirect to Razorpay payment page
        elif payment_method == "cod":
            return redirect("cod_payment")  # Redirect to COD handling
    
    return redirect("cart_view")  # Redirect if payment method is invalid



@login_required
def order_success(request):
    return render(request, "bookstore/order_success.html")

def razorpay_payment(request):
    total_price = 100  # Replace this with the actual total price logic
    
    payment = razorpay_client.order.create({
        "amount": int(total_price * 100),  # Razorpay expects amount in paise
        "currency": "INR",
        "payment_capture": "1"
    })
    
    return render(request, "bookstore/razorpay_payment.html", {"payment": payment})
def razorpay_payment(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.book.price * item.quantity for item in cart_items)  # Calculate total price
 
    payment = razorpay_client.order.create({
        "amount": int(total_price * 100),  # Razorpay expects amount in paise
        "currency": "INR",
        "payment_capture": "1"
    })
 
    return render(request, "bookstore/razorpay_payment.html", {"payment": payment})


def razorpay_payment(request):
    try:
        if not request.user.is_authenticated:
            return redirect("login")  # ✅ Redirect unauthenticated users
        
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return render(request, "bookstore/razorpay_payment.html", {
                "error": "Your cart is empty. Please add items before checkout."
            })  # ✅ Handle empty cart scenario

        # ✅ Calculate the total price from cart items
        total_price = sum(item.book.price * item.quantity for item in cart_items)
        amount = int(total_price * 100)  # ✅ Convert to paise (integer)

        # ✅ Create Razorpay order
        order_data = {
            "amount": amount,
            "currency": "INR",
            "receipt": f"order_receipt_{user.id}",
            "payment_capture": 1  # Auto capture payment
        }
        order = razorpay_client.order.create(order_data)

        return render(request, "bookstore/razorpay_payment.html", {
            "order_id": order.get("id"),  # ✅ Ensure order ID is retrieved safely
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": total_price  # ✅ Display price in rupees
        })

    except Exception as e:
        return render(request, "bookstore/razorpay_payment.html", {
            "error": f"Payment error: {str(e)}"
        })  # ✅ Handle any errors
def razorpay_verify(request):
    """Verifies Razorpay payment and processes the order if successful."""
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    if request.method == "POST":
        try:
            data = request.POST
            razorpay_order_id = data.get("razorpay_order_id")
            razorpay_payment_id = data.get("razorpay_payment_id")
            razorpay_signature = data.get("razorpay_signature")

            logger.info(f"🔹 Verifying payment for Order ID: {razorpay_order_id}")

            # Validate the payment signature before processing the order
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(params_dict)

            # Fetch user from session
            user_id = request.session.get("user_id")
            user = User.objects.get(id=user_id) if user_id else None

            if not user:
                logger.warning("⚠ User session expired during payment verification.")
                return HttpResponse("User session expired, please login again.", status=400)

            # ✅ Create orders in the database
            cart_items = Cart.objects.filter(user=user)
            print(cart_items)

            for item in cart_items:
                Order.objects.create(
                    user=user,
                    book=item.book,
                    quantity=item.quantity,
                    total_price=item.book.price * item.quantity,
                    payment_method="Razorpay",
                    payment_status="Paid"
                )

                # ✅ Reduce stock after successful payment
                item.book.stock -= item.quantity
                item.book.save()

            # ✅ Clear the cart after successful payment
            cart_items.delete()

            logger.info(f"✅ Payment verified successfully for User ID: {user_id}. Redirecting to order success page.")
            return redirect("order_success")

        except razorpay.errors.SignatureVerificationError:
            logger.error("❌ Payment verification failed due to signature mismatch.")
            return HttpResponse("Payment verification failed!", status=400)
        
        except Exception as e:
            logger.error(f"❌ Razorpay Payment Error: {str(e)}")
            return HttpResponse(f"Payment Failed: {str(e)}", status=400)

    return HttpResponse("Invalid request", status=400)

@login_required
def cod_payment(request):
    if request.method == "POST":
        user = request.user
        cart_items = user.cart_items.all()  # Get all cart items for the user

        if not cart_items:
            return redirect("order_success")  # ✅ Redirect to Order Success even if cart is empty

        for cart_item in cart_items:
            order = Order.objects.create(
                user=user,
                book=cart_item.book,
                quantity=cart_item.quantity,
                total_price=cart_item.calculate_total(),
                status="Pending",
            )

            # Create a payment record for COD
            Payment.objects.create(
                order=order,
                payment_method="COD",
                payment_status="Pending",  # COD remains pending until delivered
            )

        # ✅ Clear cart items after placing the order
        cart_items.delete()

        # ✅ Redirect **only** to order success
        return redirect("order_success")  

    # ✅ Redirect GET requests to order success page
    return redirect("order_success")
def test_razorpay_connection(request):
    # Create a Razorpay client instance
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        # Try creating an order to check if the credentials are working
        response = razorpay_client.order.create({
            "amount": 1000,  # Specify any valid amount for testing
            "currency": "INR",
            "receipt": "order_receipt_1"
        })
        return JsonResponse({"status": "success", "message": "Razorpay connection is successful!", "response": response})

    except razorpay.errors.BadRequestError as e:
        return JsonResponse({"status": "error", "message": f"Authentication failed: {e}"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"An error occurred: {e}"})
    
    

def order_success(request):
    try:
        return render(request, "bookstore/order_success.html")
    except Exception as e:
        return HttpResponse(f"Error: {e}")  # Debugging error message
def my_orders(request):
    orders = Order.objects.select_related('book').filter(user=request.user)

    print("Fetched Orders:")
    for order in orders:
        print(f"Order ID: {order.id}, Book: {order.book}, Image: {order.book.image if order.book else 'No Image'}")

    return render(request, 'my_orders.html', {'orders': orders})



@login_required
def add_book(request):
    if request.method == "POST":
        title = request.POST.get("title")
        author = request.POST.get("author")
        category_name = request.POST.get("category")  # Name instead of ID
        description = request.POST.get("description")
        image = request.FILES.get("image")

        # Ensure seller is logged in
        seller = request.user  

        # Convert price and stock safely
        try:
            price = float(request.POST.get("price"))
            stock = int(request.POST.get("stock", 10))  # Default stock = 10
        except ValueError:
            return render(request, "add_book.html", {"error": "Invalid price or stock!"})

        # Fetch category by name
        category = Category.objects.filter(name=category_name).first()
        if not category:
            return render(request, "add_book.html", {"error": "Invalid category selected!"})

        # Debugging - Print received data
        print(f"📌 Received Data: Title={title}, Author={author}, Price={price}, Category={category_name}, Stock={stock}")

        # Save the book
        book = Book(
            title=title,
            author=author,
            price=price,
            category=category,
            description=description,
            stock=stock,
            image=image,
            seller=seller  # Store seller info
        )
        book.save()
        print("✅ Book saved successfully!")

        messages.success(request, "Book published successfully!")
        return redirect("seller_dashboard")  # Redirect after adding

    categories = Category.objects.all()
    return render(request, "add_book.html", {"categories": categories})
def seller_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        store_name = request.POST.get("store_name")

        if not confirm_password:
            messages.error(request, "Confirm Password field is missing.")
            return redirect("seller_signup")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("seller_signup")

        # Check if username is already taken
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("seller_signup")

        # ✅ Create User and SellerProfile
        user = User.objects.create_user(username=username, password=password)
        seller_profile = SellerProfile.objects.create(user=user, store_name=store_name)  # Create seller profile
        user.save()
        seller_profile.save()

        messages.success(request, "Seller account created successfully. Please log in.")
        return redirect("seller_login")  # Redirect to login page after signup

    return render(request, "seller_signup.html")

def seller_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # ✅ Check if user has a SellerProfile
            if not SellerProfile.objects.filter(user=user).exists():
                messages.error(request, "You are not registered as a seller.")
                return redirect("seller_login")

            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("seller_dashboard")  # Redirect to seller dashboard
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("seller_login")

    return render(request, "seller_login.html")

def seller_dashboard(request):
    seller = request.user  # Assuming seller logs in

    # Count total books added by the seller
    total_books = Book.objects.filter(seller=seller).count()

    # Count total books sold by checking completed orders (Summing quantities)
    books_sold = OrderItem.objects.filter(book__seller=seller, order__status='completed').aggregate(
        total_books_sold=Sum('quantity')  # Fixed: Using Sum instead of Count
    )['total_books_sold'] or 0

    # Count books added to cart
    total_add_to_cart = Cart.objects.filter(book__seller=seller).count()

    # Fetch monthly sales data
    raw_monthly_sales = (
        OrderItem.objects.filter(book__seller=seller, order__status='completed')
        .annotate(month=TruncMonth('order__ordered_at'))  # Ensure 'ordered_at' exists
        .values('month')
        .annotate(total=Sum('quantity'))  # Summing quantities instead of counting order items
        .order_by('month')
    )

    # Format date properly for JavaScript
    monthly_sales = [
        {"month": datetime(sale["month"]).format("Y-m"), "total": sale["total"]}
        for sale in raw_monthly_sales
    ]
    print(list(monthly_sales))

    context = {
        'total_books': total_books,
        'books_sold': books_sold,
        'total_add_to_cart': total_add_to_cart,
        'monthly_sales': monthly_sales,  # Now properly formatted
    }

    return render(request, 'seller_dashboard.html', context)

 
    

@login_required
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items.exists():
        return redirect("cart_view")

    # if request.method == "POST":
        # Create an Order instance
    order = Order.objects.create(
        user=request.user,
        total_price=sum(item.book.price * item.quantity for item in cart_items)
    )

    # Create OrderItem instances for each cart item
    for item in cart_items:
        if item.book.stock < item.quantity:
            messages.error(request, f"Not enough stock for {item.book.title}. Available: {item.book.stock}")
            return redirect("cart_view")

        # Create an OrderItem for each book
        OrderItem.objects.create(
            order=order,
            book=item.book,
            quantity=item.quantity,
            price=item.book.price
        )

        # Reduce Stock
        item.book.stock -= item.quantity
        item.book.save()

        grand_total=sum(item.book.price * item.quantity for item in cart_items)
        cart_books=cart_items

        # Clear Cart after order is placed
        # cart_items.delete()

        # return redirect("order_success")
        return render(request, "bookstore/place_order.html", {
        "cart_items": cart_items,
        "grand_total": grand_total
        })

    return render(request, "bookstore/place_order.html", {
        "cart_items": cart_items,
        "grand_total": sum(item.book.price * item.quantity for item in cart_items)
    })



@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    order_data = []

    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        items = []

        for item in order_items:
            subtotal = item.price * item.quantity
            items.append({
                'book': item.book,
                'quantity': item.quantity,
                'price': item.price,
                'subtotal': subtotal,
            })

        order_data.append({
            'order': order,
            'order_items': items,
            'num_books': sum(item['quantity'] for item in items),
        })

    return render(request, 'bookstore/my_orders.html', {'orders': order_data})




def submit_review(request, book_id):
    book = Book.objects.get(id=book_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')  # Assuming a POST request with a rating
        Review.objects.create(book=book, user=request.user, rating=rating)
        return redirect('book_details', book_id=book.id)  # Redirect to book details page

# def payment_details(request):
#     # This is just a placeholder; replace it with actual logic if necessary
#     return render(request, 'bookstore/payment_details.html', {})


@login_required
def seller_books(request):
    seller = request.user
    books = Book.objects.filter(seller=seller)
    return render(request, "seller_books.html", {"books": books})

@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, seller=request.user)

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully!")
            return redirect("seller_books")
    else:
        form = BookForm(instance=book)

    return render(request, "edit_book.html", {"form": form})
@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, seller=request.user)
    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully!")
        return redirect("seller_books")
    return render(request, "confirm_delete.html", {"book": book})

def seller_logout(request):
    logout(request)
    return redirect('home')

from django.contrib.auth import logout
from django.shortcuts import redirect

def Buyer_logout(request):
    logout(request)
    return redirect('login') 



def admin_book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'admin_book_detail.html', {'book': book})

def admin_delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return redirect('admin_dashboard')  # Or wherever you want to redirect



def view_sellers(request):
    sellers = SellerProfile.objects.all()
    return render(request, 'view_sellers.html', {'sellers': sellers})
def delete_seller(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    seller.delete()
    return redirect('view_sellers')  #

def admin_view_orders(request):
     # Or render a forbidden page

    orders = Order.objects.all().order_by('-ordered_at')  # Admin sees all orders
    order_data = []

    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        items = []

        for item in order_items:
            subtotal = item.price * item.quantity
            items.append({
                'book': item.book,
                'quantity': item.quantity,
                'price': item.price,
                'subtotal': subtotal,
            })

        order_data.append({
            'order': order,
            'order_items': items,
            'num_books': sum(item['quantity'] for item in items),
        })

    return render(request, 'bookstore/admin_orders.html', {'orders': order_data})


def review_page(request, book_id, order_id):
    book = get_object_or_404(Book, id=book_id)
    order = get_object_or_404(Order, id=order_id)
    ratings = range(1, 6)
    review_text = request.POST.get('review_text')  

    if request.method == 'POST':
        review_text = request.POST.get('review_text')
        rating = request.POST.get('rating')
        image = request.FILES.get('image')  # optional

        # Save the review with rating
        review = Review.objects.create(
            book=book,
            user=request.user,
            rating=rating,  # <-- Add this line
            review_text=review_text,
            image=image,
        )

        messages.success(request, "Your review has been submitted.")
        return redirect('my_orders')  # or wherever you want to redirect

    return render(request, 'review_page.html', {
        'book': book,
        'order': order,
        'ratings': ratings
    })


def admin_reviews(request):
    reviews = Review.objects.all()  # Get all reviews
    return render(request, 'admin_reviews.html', {'reviews': reviews})


def admin_view_buyers(request):
    buyers =Buyer.objects.all()
    return render(request, 'admin_buyers.html', {'buyers': buyers})
def delete_buyer(request, buyer_id):
    buyers = get_object_or_404(Seller, id=buyer_id)
    buyers.delete()
    return redirect('admin_buye')  #