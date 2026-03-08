from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.HomeView.as_view(), name='listing'),
    path('listing/<int:pk>/', views.ListingDetailView.as_view(), name='listing_detail'),
    path('create/', views.ListingCreateView.as_view(), name='listing_create'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('my-listings/', views.MyListingsView.as_view(), name='my_listings'),
    path('favorites/', views.FavoriteListView.as_view(), name='favorite_listings'),
    path('toggle-favorite/<int:pk>/', views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('admin/', admin.site.urls) 
]