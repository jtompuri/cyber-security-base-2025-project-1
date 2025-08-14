from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import connection
from .models import ShortenedURL, ClickLog
import json

def home(request):
    """Home page with URL shortening form"""
    return render(request, 'shortener/home.html')

# FLAW #1: Missing CSRF protection
@csrf_exempt
def shorten_url(request):
    """Create a shortened URL - VULNERABLE to CSRF attacks"""
    if request.method == 'POST':
        original_url = request.POST.get('url', '')
        notes = request.POST.get('notes', '')
        
        if not original_url:
            return JsonResponse({'error': 'URL is required'}, status=400)
        
        short_code = ShortenedURL.generate_short_code()
        shortened = ShortenedURL.objects.create(
            original_url=original_url,
            short_code=short_code,
            created_by=request.user if request.user.is_authenticated else None,
            notes=notes
        )
        
        return JsonResponse({
            'short_url': f"{request.get_host()}/s/{short_code}",
            'short_code': short_code
        })
    
    return render(request, 'shortener/home.html')

# FIX: Remove @csrf_exempt and add {% csrf_token %} to forms
# SECURE VERSION:
# def shorten_url(request):
#     """Create a shortened URL - SECURE VERSION"""
#     if request.method == 'POST':
#         original_url = request.POST.get('url', '')
#         notes = request.POST.get('notes', '')
        
#         if not original_url:
#             return JsonResponse({'error': 'URL is required'}, status=400)
        
#         short_code = ShortenedURL.generate_short_code()
#         shortened = ShortenedURL.objects.create(
#             original_url=original_url,
#             short_code=short_code,
#             created_by=request.user if request.user.is_authenticated else None,
#             notes=notes
#         )
        
#         return JsonResponse({
#             'short_url': f"{request.get_host()}/s/{short_code}",
#             'short_code': short_code
#         })
    
#     return render(request, 'shortener/home.html')

# FLAW #2: SQL injection vulnerability
def search_urls(request):
    """Search URLs - VULNERABLE to SQL injection"""
    query = request.GET.get('q', '')
    if query:
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM shortener_shortenedurl WHERE original_url LIKE '%{query}%'"
            cursor.execute(sql)
            results = cursor.fetchall()
        
        urls = []
        for row in results:
            urls.append({
                'id': row[0],
                'original_url': row[1],
                'short_code': row[2],
                'created_at': row[4]
            })
        
        return JsonResponse({'urls': urls})
    
    return JsonResponse({'urls': []})

# FIX: Use parameterized queries - ShortenedURL.objects.filter(original_url__icontains=query)
# SECURE VERSION:
# def search_urls(request):
#     """Search URLs - SECURE VERSION using Django ORM"""
#     query = request.GET.get('q', '')
#     if query:
#         # Use Django ORM to prevent SQL injection
#         urls_queryset = ShortenedURL.objects.filter(
#             original_url__icontains=query
#         ).values('id', 'original_url', 'short_code', 'created_at')
        
#         urls = list(urls_queryset)
#         return JsonResponse({'urls': urls})
    
#     return JsonResponse({'urls': []})

def redirect_url(request, short_code):
    """Redirect to original URL and log the click"""
    try:
        shortened = get_object_or_404(ShortenedURL, short_code=short_code, is_active=True)
        
        # Log the click
        ClickLog.objects.create(
            shortened_url=shortened,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referer=request.META.get('HTTP_REFERER', '')
        )
        
        # Update click count
        shortened.click_count += 1
        shortened.save()
        
        return redirect(shortened.original_url)
    except ShortenedURL.DoesNotExist:
        return render(request, 'shortener/404.html', status=404)

def my_urls(request):
    """Display user's URLs"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    urls = ShortenedURL.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'shortener/my_urls.html', {'urls': urls})

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# FLAW #3: Insecure Direct Object References
def url_details(request, url_id):
    """View URL details - VULNERABLE to unauthorized access"""
    try:
        url = ShortenedURL.objects.get(id=url_id)
        clicks = ClickLog.objects.filter(shortened_url=url).order_by('-clicked_at')[:10]
        
        return render(request, 'shortener/url_details.html', {
            'url': url,
            'clicks': clicks
        })
    except ShortenedURL.DoesNotExist:
        return render(request, 'shortener/404.html', status=404)

# FIX: Add @login_required and check url.created_by == request.user
# SECURE VERSION:
# @login_required
# def url_details(request, url_id):
#     """View URL details - SECURE VERSION with proper access control"""
#     try:
#         # Only allow users to view their own URLs
#         url = ShortenedURL.objects.get(id=url_id, created_by=request.user)
#         clicks = ClickLog.objects.filter(shortened_url=url).order_by('-clicked_at')[:10]
        
#         return render(request, 'shortener/url_details.html', {
#             'url': url,
#             'clicks': clicks
#         })
#     except ShortenedURL.DoesNotExist:
#         return render(request, 'shortener/404.html', status=404)

# FLAW #4: Weak session management and missing CSRF protection
@csrf_exempt
def simple_login(request):
    """Simple login - VULNERABLE to session fixation and CSRF attacks"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            request.session.set_expiry(0)  # Session expires when browser closes
            return redirect('home')
        else:
            return render(request, 'shortener/login.html', {
                'error': 'Invalid credentials'
            })
    
    return render(request, 'shortener/login.html')

# FIX: Remove @csrf_exempt, add proper session management with request.session.cycle_key()
# SECURE VERSION:
# def simple_login(request):
#     """Simple login - SECURE VERSION"""
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
        
#         user = authenticate(request, username=username, password=password)
#         if user:
#             # Regenerate session key to prevent session fixation
#             request.session.cycle_key()
#             login(request, user)
#             return redirect('home')
#         else:
#             return render(request, 'shortener/login.html', {
#                 'error': 'Invalid credentials'
#             })
    
#     return render(request, 'shortener/login.html')

def simple_logout(request):
    """Logout the user"""
    logout(request)
    return redirect('home')
