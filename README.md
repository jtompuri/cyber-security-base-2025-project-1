# Vulnerable URL Shortener

This Django application demonstrates 5 critical security vulnerabilities from the OWASP Top 10 2021 for educational purposes.

## Vulnerabilities Demonstrated

### FLAW 1: 
Missing CSRF Protection (A04:2021 - Insecure Design)

**Location:** https://github.com/jtompuri/cyber-security-base-2025-project-1/blob/main/shortener/views.py#L15
**Issue:** `@csrf_exempt` decorator removes CSRF protection  
**Impact:** Attackers can create malicious forms to submit URLs without user consent  
**Fix:** Remove `@csrf_exempt`, add `{% csrf_token %}` to forms

### FLAW 2: 
SQL Injection (A03:2021 - Injection)

**Location:** https://github.com/jtompuri/cyber-security-base-2025-project-1/blob/main/shortener/views.py#L43
**Issue:** Direct string interpolation in SQL queries  
**Impact:** Database manipulation, data theft  
**Fix:** Use Django ORM: `ShortenedURL.objects.filter(original_url__icontains=query)`

### FLAW 3: 
Broken Access Control (A01:2021 - Broken Access Control)

**Location:** https://github.com/jtompuri/cyber-security-base-2025-project-1/blob/main/shortener/views.py#L106
**Issue:** No authorization checks for URL details  
**Impact:** Users can view any URL's private details  
**Fix:** Add `@login_required` and filter by `created_by=request.user`

### FLAW 4: 
Weak Authentication (A07:2021 - Authentication Failures)

**Location:** https://github.com/jtompuri/cyber-security-base-2025-project-1/blob/main/shortener/views.py#L122
**Issue:** Missing CSRF protection, no session regeneration, weak settings  
**Impact:** Session fixation, brute force attacks  
**Fix:** Remove `@csrf_exempt`, use `request.session.cycle_key()`, add rate limiting

### FLAW 5: 
Security Misconfiguration (A05:2021 - Security Misconfiguration)

**Location:** https://github.com/jtompuri/cyber-security-base-2025-project-1/blob/main/project/settings.py#L25
**Issue:** Debug mode enabled, weak session settings, verbose logging  
**Impact:** Information disclosure, session vulnerabilities  
**Fix:** Set `DEBUG = False`, configure secure session settings

The application runs with `DEBUG = True` and `ALLOWED_HOSTS = ['*']` in production-like settings. Debug mode exposes sensitive system information, detailed error messages, and internal application structure to users when errors occur. The permissive ALLOWED_HOSTS setting allows the application to serve requests from any hostname, potentially enabling Host header injection attacks.

**How to fix it:**
Set `DEBUG = False` for production, configure `ALLOWED_HOSTS` to include only legitimate domain names (e.g., `['yourdomain.com', 'www.yourdomain.com']`), implement proper error pages that don't expose sensitive information, configure secure session cookie settings (`SESSION_COOKIE_SECURE = True`, `SESSION_COOKIE_HTTPONLY = True`), and set up appropriate logging that doesn't expose sensitive data.

## Installation and Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd cyber-security-base-2025-project-1
   ```

## Setup Instructions

1. **Clone the repository**
2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   ```
3. **Install dependencies:**
   ```bash
   pip install Django
   ```
4. **Run migrations:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. **Start the application:**
   ```bash
   python manage.py runserver
   ```

## Testing Vulnerabilities

### Two-Server Setup Required
- **Django Server**: `python manage.py runserver` (Port 8000)  
- **HTTP Server**: `python -m http.server 8001` (Port 8001)  

This dual-port setup is needed because browser security isolates file:// from http:// protocols, requiring the CSRF demo to run on a proper HTTP server.

### Attack Tests

**CSRF Attack**: Visit http://localhost:8001/csrf_attack_demo.html while logged into the Django app. The demo provides visual feedback when attacks succeed.

**SQL Injection**: Use the search box with: `' OR 1=1 --` (shows all URLs) or `' UNION SELECT 999,'HACKED_URL','HACK',datetime('now'),0,1,'SQL Injection',1 --` (shows fake data)

**Access Control**: Try accessing `/details/1/` while logged in as a different user

**Weak Auth**: Check login form at `/login/` - no CSRF protection or rate limiting

**Config Issues**: Visit `/nonexistent/` to see debug error pages

## Note

All vulnerabilities have fix examples commented in the source code. This is for educational purposes only.