from django.urls import path
from . import views
from .views import register_view
from .views import my_listings
from .views import logout_view
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.listing_list, name='listing'),
    path('detail/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('create/', views.listing_create, name='listing_create'),
    path('register/', register_view, name='register'),
    path('my-listings/', my_listings, name='my_listings'),
    path('logout/', logout_view, name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='listings/login.html'), name='login'),


]
