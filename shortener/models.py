from django.db import models
from django.contrib.auth.models import User
import random
import string

class ShortenedURL(models.Model):
    """Model for storing shortened URLs with intentional security flaws"""
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=10, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    click_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # FLAW #5: Storing sensitive data in plain text
    notes = models.TextField(blank=True, help_text="Private notes about this URL")
    # FIX: Use django-cryptography: EncryptTextField(blank=True)
    
    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"
    
    @classmethod
    def generate_short_code(cls):
        """Generate a random short code"""
        length = 6
        characters = string.ascii_letters + string.digits
        while True:
            short_code = ''.join(random.choice(characters) for _ in range(length))
            if not cls.objects.filter(short_code=short_code).exists():
                return short_code

class ClickLog(models.Model):
    """Model for tracking clicks on shortened URLs"""
    shortened_url = models.ForeignKey(ShortenedURL, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    clicked_at = models.DateTimeField(auto_now_add=True)
    referer = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"Click on {self.shortened_url.short_code} at {self.clicked_at}"
