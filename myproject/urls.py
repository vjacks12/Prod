"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from .views import stripe_payment, dashboard_view, home_view, login_view, register_view
from django.urls import path
from .views import stripe_payment, dashboard_view, logout_view
from .views import homepage_view
from .views import home_view  # Ensure you have a home view function



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('pay/', views.stripe_payment, name='stripe_payment'),
    path('stripe-payment/', stripe_payment, name='stripe_payment'),
    path('homepage/', homepage_view, name='homepage'),  # Make sure this line exists
    path('yourdashboard/', views.your_dashboard, name='your_dashboard'),
    path('settings/', views.settings_view, name='settings'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('process-video/', views.process_video, name='process_video'),


]



