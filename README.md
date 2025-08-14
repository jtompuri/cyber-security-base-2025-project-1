# Vulnerable URL Shortener

This Django application demonstrates 5 critical security vulnerabilities from the OWASP Top 10 2021 for the Cyber Security Base 2025 course.

## Table of Contents
- [Quick Start](#quick-start)
- [Testing Vulnerabilities](#testing-vulnerabilities)
- [Vulnerabilities Explained](#vulnerabilities-explained)

## Quick Start

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/jtompuri/cyber-security-base-2025-project-1.git
   cd cyber-security-base-2025-project-1
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install Django
   ```

4. **Set up database:**
   ```bash
   python manage.py migrate
   ```

5. **Create user accounts:**
   
   **Create superuser (admin access):**
   ```bash
   python manage.py createsuperuser
   ```
   - Username: `admin`
   - Password: `admin` (or your preference)
   - Email: (optional)

   **Create test user (vulnerability demonstrations):**
   ```bash
   echo "from django.contrib.auth.models import User; User.objects.create_user('attacker', 'attacker@example.com', 'password123')" | python manage.py shell
   ```

6. **Start the application:**

   **Two-Server Setup (Required for vulnerability testing):**
   ```bash
   # Terminal 1: Start Django server
   python manage.py runserver
   
   # Terminal 2: Start HTTP server (run from project root directory)
   python -m http.server 8001
   ```

   Browser security policies prevent file:// protocol from accessing http:// protocols. The CSRF attack demo needs a proper HTTP server.

   **Access Points:**
   - Django Application: http://localhost:8000
   - CSRF Demo: http://localhost:8001/csrf_attack_demo.html

## Testing Vulnerabilities

### Prerequisites

**Test Accounts:**
- **Admin**: `admin` / `admin` (admin panel access and general testing)
- **Attacker**: `attacker` / `password123` (multi-user vulnerability testing)

Needed to demonstrate access control vulnerabilities and cross-user attacks.

**Check Server Status:**
- Django server running at http://localhost:8000
- HTTP server running at http://localhost:8001
- Both test accounts created

### Attack Demonstrations

#### 1. CSRF Attack Testing
**Setup:** Visit http://localhost:8001/csrf_attack_demo.html while logged into Django (http://localhost:8000)

**Attack #1 - URL Creation:** Creates malicious URLs in victim's account  
**Attack #2 - Login/Session Fixation:** Logs victim into attacker's account

**What Happens:** 
- Forms submit to hidden iframes for seamless demonstration
- Real-time feedback shows attack status on demo page
- No browser redirects - stay on demo page throughout testing
- Demonstrates core CSRF vulnerabilities with immediate verification

#### 2. SQL Injection Testing
**Basic Test:** Search with `' OR 1=1 --`
- **Result:** Shows ALL URLs (bypasses search filter)
- **Why:** `OR 1=1` is always true

**Advanced Test:** Try `' UNION SELECT 999,'HACKED_URL','HACK',datetime('now'),0,1,'SQL Injection',1 --`
- **Result:** Fake data mixed with real results
- **Purpose:** Demonstrates data injection techniques

**Data Extraction:** Use `' UNION SELECT id,username,email,date_joined,0,1,'EXTRACTED',1 FROM auth_user --`
- **Result:** Extracts user credentials
- **Impact:** Shows severity of SQL injection

#### 3. Broken Access Control Testing
**Method:** Try URLs `/details/1/`, `/details/2/`, `/details/3/`

**Observations:**
- Can view any URL details regardless of ownership
- Works even when logged out (some details)
- Access to click analytics, IP addresses, usage patterns

**Real-World Test:**
1. Create account, shorten URL (note the ID)
2. Switch to different user account
3. Access first user's URL by changing ID in URL

#### 4. Authentication Testing
**Session Fixation Test:**
1. Open Developer Tools → Network tab
2. Note session ID before login
3. Log in and check if session ID changes
4. **Expected (Vulnerable):** Session ID stays same
5. **Secure Behavior:** Session ID should change

**CSRF Login Test:**
- Login form lacks CSRF protection
- Enables malicious login forms
- Users could unknowingly use attacker accounts

#### 5. Security Misconfiguration Testing
**Debug Info Exposure:**
- Visit `/nonexistent-page/` for 404 debug page
- **Observe:** File paths, installed packages, system details
- **Risk:** Information aids further attacks

**Session Cookie Analysis:**
1. Developer Tools → Application → Cookies
2. Examine Django session cookie
3. **Missing:** `Secure`, `HttpOnly`, `SameSite` flags
4. **Risk:** Cookie theft and CSRF attacks
