from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import logout_confirm, CustomLogoutView

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
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/bookings/', views.user_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('logout/confirm/', logout_confirm, name='logout_confirm'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password_reset/',
         views.CustomPasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',views.CustomPasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='tickets/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='tickets/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='tickets/password_change.html'
         ),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='tickets/password_change_done.html'
         ),
         name='password_change_done'),
    path('profile/edit/username/', views.edit_username, name='edit_username'),
    path('profile/edit/email/', views.edit_email, name='edit_email'),
    path('profile/edit/full-name/', views.edit_full_name, name='edit_full_name'),
    path('profile/edit/phone/', views.edit_phone, name='edit_phone'),
]
