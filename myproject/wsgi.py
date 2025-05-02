"""
WSGI config for myproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Ensure the project directory is in the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables for Razorpay (ensure they are available for the WSGI application)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
os.environ.setdefault('RAZORPAY_KEY_ID', 'rzp_test_nOCkgcInzdldXa')
os.environ.setdefault('RAZORPAY_KEY_SECRET', 'dDwlRvBJsUptegrJ31XC1io4')

# Initialize the WSGI application
application = get_wsgi_application()
