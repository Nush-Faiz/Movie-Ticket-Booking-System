from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('upcoming/<int:movie_id>/', views.upcoming_movie_detail, name='upcoming_detail'),
    path('book/<int:showtime_id>/', views.book_ticket, name='book_ticket'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('about-us/', views.about_us, name='about_us'),
    path('faqs/', views.faqs, name='faqs'),
    path('feedback/', views.feedback, name='feedback'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.user_profile, name='profile'),
]
