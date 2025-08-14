# Vulnerable URL Shortener

This Django application demonstrates 5 critical security vulnerabilities from the OWASP Top 10 2021 for the Cyber Security Base 2025 course.

## Vulnerabilities Demonstrated

### FLAW 1: Missing CSRF Protection (A04:2021 - Insecure Design)
**Location:** https://github.com/jtompuri/cyber-security-base-2025-project-1/blob/main/shortener/views.py#L15  

**Detailed Issue:** The `shorten_url()` function uses the `@csrf_exempt` decorator, which completely disables Django's built-in Cross-Site Request Forgery protection. CSRF attacks occur when malicious websites trick authenticated users into performing unintended actions on trusted sites where they're logged in.

**Technical Explanation:** Without CSRF protection, an attacker can create a malicious HTML form on their website that submits POST requests to the vulnerable application. When a logged-in user visits the attacker's site, their browser automatically includes session cookies, making the request appear legitimate.

**Attack Scenario:** An attacker creates a hidden form at `http://evil-site.com` that posts to `http://vulnerable-site.com/shorten/` with malicious URL data. When users visit the evil site, URLs are created in their account without consent.

**Impact:** 
- Unauthorized URL creation in victim accounts
- Potential for creating phishing or malware URLs under trusted user accounts  
- Reputation damage and abuse of the service

**Fix:** Remove `@csrf_exempt`, add `{% csrf_token %}` to forms
**Link to fix:** https://github.com/jtompuri/cyber-security-base-2025-project-1/blob/main/shortener/views.py#L41

---

### FLAW 2: SQL Injection (A03:2021 - Injection)
**Location:** https://github.com/jtompuri/cyber-security-base-2025-project-1/blob/main/shortener/views.py#L43  

**Detailed Issue:** The `search_urls()` function constructs SQL queries using string concatenation with user input, creating a classic SQL injection vulnerability. The dangerous line: `sql = f"SELECT * FROM shortener_shortenedurl WHERE original_url LIKE '%{query}%'"`

**Technical Explanation:** SQL injection occurs when user input is directly inserted into SQL queries without proper sanitization or parameterization. Attackers can break out of the intended query structure and execute arbitrary SQL commands.

**Attack Scenario:** 
- Input: `' OR 1=1 --` returns all URLs in the database
- Input: `'; DROP TABLE shortener_shortenedurl; --` could delete the entire URL table
- Input: `' UNION SELECT username,password,email FROM auth_user --` could extract user credentials

**Impact:**
- Complete database compromise (read, modify, delete data)
- Unauthorized access to sensitive information
- Potential server takeover in severe cases
- Data exfiltration and privacy violations

**Fix:** Use Django ORM: `ShortenedURL.objects.filter(original_url__icontains=query)`

---

### FLAW 3: Broken Access Control (A01:2021 - Broken Access Control)
**Location:** https://github.com/jtompuri/cyber-security-base-2025-project-1/blob/main/shortener/views.py#L106  

**Detailed Issue:** The `url_details()` function displays URL details and click analytics for any URL ID without checking if the requesting user owns that URL. This is a classic Insecure Direct Object Reference (IDOR) vulnerability.

**Technical Explanation:** The function accepts a URL ID parameter and directly queries the database without authorization checks. Any authenticated or even unauthenticated user can view any URL's sensitive details by simply changing the ID in the URL path.

**Attack Scenario:** 
- User creates account and shortens a URL, getting ID 5
- User changes URL from `/details/5/` to `/details/1/`, `/details/2/`, etc.
- User gains access to other users' private URLs, click analytics, IP addresses, and usage patterns

**Impact:**
- Privacy violations (viewing others' URLs and analytics)
- Business intelligence leakage (understanding competitor activity)
- Personal information exposure (IP addresses, user agents, referrers)
- Potential for further attacks using gathered intelligence

**Fix:** Add `@login_required` and filter by `created_by=request.user`

---

### FLAW 4: Weak Authentication (A07:2021 - Authentication Failures)
**Location:** https://github.com/jtompuri/cyber-security-base-2025-project-1/blob/main/shortener/views.py#L122  

**Detailed Issue:** The `simple_login()` function has multiple authentication vulnerabilities: missing CSRF protection, no session regeneration after login, and weak session configuration settings.

**Technical Explanation:** 
1. **Session Fixation:** Without `request.session.cycle_key()`, attackers can set a user's session ID before they log in, then hijack their session post-authentication
2. **CSRF on Login:** The `@csrf_exempt` decorator makes the login form vulnerable to cross-site request forgery
3. **Weak Session Settings:** Long session timeouts, insecure cookies, and missing security headers

**Attack Scenario:**
- Attacker sends victim a link with a preset session ID
- Victim logs in using that session ID  
- Attacker uses the known session ID to impersonate the victim
- Or: Attacker creates malicious login forms that log users into attacker-controlled accounts

**Impact:**
- Account takeover through session fixation
- Unauthorized access to user accounts
- Identity theft and impersonation
- Data breach and privacy violations

**Fix:** Remove `@csrf_exempt`, use `request.session.cycle_key()`, add rate limiting

---

### FLAW 5: Security Misconfiguration (A05:2021 - Security Misconfiguration)
**Location:** https://github.com/jtompuri/cyber-security-base-2025-project-1/blob/main/project/settings.py#L25  

**Detailed Issue:** The application runs with `DEBUG = True` and `ALLOWED_HOSTS = ['*']` in production-like settings. Debug mode exposes sensitive system information, detailed error messages, and internal application structure to users when errors occur. The permissive ALLOWED_HOSTS setting allows the application to serve requests from any hostname, potentially enabling Host header injection attacks.

**Technical Explanation:**
1. **Debug Mode:** Exposes detailed error pages with stack traces, variable values, and system information
2. **Permissive ALLOWED_HOSTS:** Enables Host header injection attacks
3. **Insecure Session Cookies:** Missing `Secure`, `HttpOnly`, and `SameSite` flags
4. **Verbose Logging:** DEBUG level logging may expose sensitive data in log files

**Attack Scenario:**
- Attacker triggers errors to view debug pages revealing system internals, file paths, and configuration
- Host header injection redirects users to malicious sites
- Session cookie theft via XSS (no HttpOnly flag)
- Man-in-the-middle attacks (no Secure flag for HTTPS-only cookies)

**Impact:**
- Information disclosure of system architecture and sensitive data
- Session hijacking and account takeover
- Cache poisoning and redirect attacks
- Compliance violations (GDPR, PCI DSS, etc.)

**Fix:** Set `DEBUG = False` for production, configure `ALLOWED_HOSTS` to include only legitimate domain names (e.g., `['yourdomain.com', 'www.yourdomain.com']`), implement proper error pages that don't expose sensitive information, configure secure session cookie settings (`SESSION_COOKIE_SECURE = True`, `SESSION_COOKIE_HTTPONLY = True`), and set up appropriate logging that doesn't expose sensitive data.

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

### Prerequisites
**Two-Server Setup Required:**
- **Django Server**: `python manage.py runserver` (Port 8000)  
- **HTTP Server**: `python -m http.server 8001` (Port 8001)  

This dual-port setup is essential because browser security policies isolate file:// protocol from http:// protocols, requiring the CSRF attack demonstration to run on a proper HTTP server.

### Detailed Attack Demonstrations

#### 1. CSRF Attack Testing
**Setup:** Visit http://localhost:8001/csrf_attack_demo.html while logged into the Django app (http://localhost:8000)

**What Happens:** 
- The demo page contains a hidden form that automatically submits to the Django app
- Creates malicious URLs in the logged-in user's account without consent
- Demonstrates how CSRF attacks work in real-world scenarios
- Visual feedback shows when attacks succeed with "Attack Successful!" messages

#### 2. SQL Injection Testing
**Basic Injection:** Use the search box with `' OR 1=1 --`
- **Expected Result:** Shows all URLs in the database regardless of search term
- **Why it works:** The OR 1=1 condition is always true, bypassing the WHERE clause

**Advanced Injection:** Use `' UNION SELECT 999,'HACKED_URL','HACK',datetime('now'),0,1,'SQL Injection',1 --`
- **Expected Result:** Shows fake data mixed with real results
- **Why it works:** UNION combines fake data with legitimate query results
- **Educational Note:** Demonstrates data exfiltration techniques

**Data Extraction:** Try `' UNION SELECT id,username,email,date_joined,0,1,'EXTRACTED',1 FROM auth_user --`
- **Purpose:** Shows how attackers extract sensitive user data
- **Impact:** Reveals the severity of SQL injection vulnerabilities

#### 3. Broken Access Control Testing
**Method:** Try accessing `/details/1/`, `/details/2/`, `/details/3/` etc.
- **What to observe:** You can view any URL's details regardless of ownership
- **Test while logged out:** Some details may still be accessible
- **Privacy violation:** View other users' click analytics, IP addresses, and usage patterns

**Real-world simulation:** 
1. Create account and shorten a URL (note the ID)
2. Log in as different user 
3. Access the first user's URL details by changing the ID in the URL

#### 4. Authentication Vulnerabilities Testing
**Session Fixation Test:**
1. Open browser developer tools (Network tab)
2. Note session ID before logging in
3. Log in and check if session ID changes
4. **Expected:** Session ID remains the same (vulnerable)
5. **Secure behavior:** Session ID should change after login

**CSRF on Login Test:**
- The login form lacks CSRF protection
- Attackers could create malicious login forms
- Users might unknowingly log into attacker-controlled accounts

#### 5. Security Misconfiguration Testing
**Debug Information Exposure:**
- Visit `/nonexistent-page/` to trigger 404 debug page
- **Observe:** Detailed error information, file paths, installed packages
- **Security risk:** Information disclosure aids further attacks

**Session Cookie Analysis:**
1. Open browser developer tools → Application → Cookies
2. Examine Django session cookie properties
3. **Observe:** Missing `Secure`, `HttpOnly`, and `SameSite` flags
4. **Risk:** Cookies vulnerable to theft and CSRF attacks

### Security Testing Tools
For advanced testing, consider using:
- **SQLMap:** Automated SQL injection testing
- **Burp Suite:** Web application security testing
- **OWASP ZAP:** Free security testing proxy
- **Browser Developer Tools:** Cookie and session analysis

## Educational Purpose & Implementation Notes

### Code Organization
All vulnerabilities have corresponding fix examples commented in the source code with detailed explanations:
- **Vulnerable code:** Actively demonstrates security flaws
- **Secure alternatives:** Commented code shows proper implementation
- **Educational comments:** Explain why vulnerabilities exist and how to prevent them

### Learning Objectives
This application teaches:
1. **Recognition:** How to identify common security vulnerabilities
2. **Exploitation:** Understanding attacker techniques and methodologies  
3. **Prevention:** Implementing secure coding practices
4. **Defense:** Configuring applications securely

### Security Best Practices Demonstrated
- **Input Validation:** Proper sanitization and parameterized queries
- **Authentication:** Secure session management and CSRF protection
- **Authorization:** Proper access controls and permission checks
- **Configuration:** Production-ready security settings
- **Logging:** Appropriate log levels without information disclosure

### Real-World Application
These vulnerabilities are commonly found in production applications:
- **OWASP Top 10 Compliance:** Based on the most critical web application risks
- **Industry Relevance:** Reflects actual security challenges faced by developers
- **Practical Skills:** Hands-on experience with vulnerability assessment and remediation

⚠️ **Important:** This application is for educational purposes only. Never deploy vulnerable code to production environments.