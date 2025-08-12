from django.contrib import admin
from .models import ShortenedURL, ClickLog

@admin.register(ShortenedURL)
class ShortenedURLAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'original_url', 'created_by', 'created_at', 'click_count', 'is_active')
    list_filter = ('is_active', 'created_at', 'created_by')
    search_fields = ('short_code', 'original_url')
    readonly_fields = ('created_at',)

@admin.register(ClickLog)
class ClickLogAdmin(admin.ModelAdmin):
    list_display = ('shortened_url', 'ip_address', 'clicked_at')
    list_filter = ('clicked_at',)
    readonly_fields = ('clicked_at',)
