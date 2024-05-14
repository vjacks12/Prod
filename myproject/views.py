from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
import stripe
from .models import Profile
from tempfile import NamedTemporaryFile
import time
import random
from django.views.decorators.csrf import csrf_exempt
from pytube import YouTube  # Ensure this import is present

# Initialize Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                if user.profile.has_paid:
                    return redirect('homepage')
                else:
                    return redirect('dashboard')
            except Profile.DoesNotExist:
                return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': "Invalid username or password"})
    return render(request, 'login.html')

def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            if not User.objects.filter(username=username).exists():
                if not User.objects.filter(email=email).exists():
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    return redirect('dashboard')
                else:
                    return render(request, 'register.html', {'error': "Email already exists."})
            else:
                return render(request, 'register.html', {'error': "Username already exists."})
        else:
            return render(request, 'register.html', {'error': "Passwords do not match."})
    return render(request, 'register.html')

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html', {'stripe_key': settings.STRIPE_PUBLIC_KEY})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def stripe_payment(request):
    if request.method == "POST":
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': 'Test Purchase',
                            },
                            'unit_amount': 0,
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('homepage')) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(reverse('dashboard')),
            )
            return redirect(checkout_session.url)
        except stripe.error.StripeError as e:
            return render(request, 'dashboard.html', {'error': str(e)})
    return redirect('dashboard')

@login_required
def homepage_view(request):
    session_id = request.GET.get('session_id')
    if session_id:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            profile, _ = Profile.objects.get_or_create(user=request.user)
            profile.has_paid = True
            profile.save()
            return render(request, 'homepage.html')
    try:
        if request.user.profile.has_paid:
            return render(request, 'homepage.html')
        else:
            return redirect('dashboard')
    except Profile.DoesNotExist:
        return redirect('dashboard')

@login_required
def your_dashboard(request):
    try:
        if request.user.profile.has_paid:
            return render(request, 'yourdashboard.html')
        else:
            return redirect('homepage')
    except Profile.DoesNotExist:
        return redirect('register')

@login_required
def settings_view(request):
    if not request.user.profile.has_paid:
        return redirect('homepage')
    return render(request, 'settings.html')

@login_required
def analytics_view(request):
    if not request.user.profile.has_paid:
        return redirect('homepage')
    return render(request, 'analytics.html')

def fetch_youtube_stream(video_url, max_retries=5):
    for attempt in range(max_retries):
        try:
            yt = YouTube(video_url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            return stream
        except Exception as e:
            if "HTTP Error 429" in str(e):
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(sleep_time)
            else:
                raise e
    raise Exception("Failed to fetch YouTube stream after multiple attempts")

from .tasks import process_video_task

@login_required
def process_video(request):
    if request.method == "POST":
        video_url = request.POST.get('video_url')
        if not video_url:
            return HttpResponse("No video URL provided", status=400)

        result = process_video_task.delay(video_url)
        return HttpResponse(f"Video processing started. Task ID: {result.id}")

    return redirect('your_dashboard')
