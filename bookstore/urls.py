from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView  # ✅ Import Django's LogoutView
from .views import razorpay_payment
from .views import order_success
from .views import razorpay_client
from .views import my_orders
from .views import add_to_cart
from .views import search_books
from .views import add_book
from bookstore.views import seller_signup, seller_login, seller_dashboard
from .views import get_admin_data
from django.conf.urls import include


  # or the correct function name

from . import views  # ✅ Import views correctly

urlpatterns = [
    # ✅ Home and Authentication Routes
    path('', views.home, name='home'),
    path('categories/', views.category_view, name='categories'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),  # ✅ User login
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),  # ✅ Proper logout handling

    # ✅ Admin Authentication
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),  
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),  
     path('get_admin_data/', get_admin_data, name='get_admin_data'),
    
    # path('payment-details/', views.payment_details, name='payment_details'),

    # ✅ Category and Book Details
    path('fiction/', views.fiction_books, name='fiction_books'),
    path('science-fiction/', views.science_fiction_books, name='science_fiction_books'),
    path('non-fiction/', views.non_fiction_books, name='non_fiction_books'),
    path('category/<str:category_name>/', views.category_books, name='category_books'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),

    # ✅ Cart Functionality
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:cart_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('cart/place-order/', views.place_order, name='place_order'),
    path('cart/add/<int:book_id>/', add_to_cart, name='add_to_cart'),

    # ✅ Search Functionality
    path('search-books/', views.search_books, name='search_books'),


     path('order-success/', order_success, name="order_success"),
     

    path('razorpay-payment/', razorpay_payment, name='razorpay_payment'),

     path('cart/process-payment/', views.process_payment, name='process_payment'),
      path('test-razorpay/', views.test_razorpay_connection, name='test_razorpay'),
      path('cod-payment/', views.cod_payment, name='cod_payment'),
       path('my-orders/', my_orders, name='my_orders'),
        path('seller/add_book/', add_book, name='add_book'),

        path('seller/signup/', seller_signup, name='seller_signup'),
    path('seller/login/', seller_login, name='seller_login'),
    path('seller/dashboard/', seller_dashboard, name='seller_dashboard'),
 path("seller/books/", views.seller_books, name="seller_books"),
    path("seller/book/edit/<int:book_id>/", views.edit_book, name="edit_book"),
    path("seller/book/delete/<int:book_id>/", views.delete_book, name="delete_book"),
    path('seller/logout/', views.seller_logout, name='seller_logout'),
    path('Buyer/logout/', views.Buyer_logout, name='buyer_logout'),
    path('dashboard/book/<int:book_id>/', views.admin_book_detail, name='abook_detail'),
path('a/book/<int:book_id>/delete/', views.admin_delete_book, name='admin_delete_book'),
path('dashboard/admin-sellers/', views.view_sellers, name='view_sellers'),
    path('dlt/sellers/delete/<int:seller_id>/', views.delete_seller, name='delete_seller'),
        path('dashboard/admin-orders/', views.admin_view_orders, name='admin_orders'),
       path('review/<int:book_id>/order/<int:order_id>/', views.review_page, name='review_page'),
       path('dashboard/admin-reviews/', views.admin_reviews, name='admin_reviews'),
         path('dashboard/buyers/', views.admin_view_buyers, name='admin_view_buyers'),
         path('dlt/buyers/delete/<int:buyer_id>/', views.delete_buyer, name='delete_seller'),
         path('bookadminv',views.admin_bookv,name="admin_bookv"),
          path('book/delete-book/<int:book_id>/', views.delete_book, name='delete_book'),
          








]


# ✅ Debug Toolbar - Only for Development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

# ✅ Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
