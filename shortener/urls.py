from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shorten/', views.shorten_url, name='shorten_url'),
    path('search/', views.search_urls, name='search_urls'),
    path('s/<str:short_code>/', views.redirect_url, name='redirect_url'),
    path('details/<int:url_id>/', views.url_details, name='url_details'),
    path('login/', views.simple_login, name='login'),
    path('logout/', views.simple_logout, name='logout'),
    path('my-urls/', views.my_urls, name='my_urls'),
]
