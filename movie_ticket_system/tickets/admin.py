from django.contrib import admin
from .models import Movie, Theater, Showtime, Booking

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_released', 'release_date', 'genre', 'rating')
    list_filter = ('is_released', 'genre', 'rating')
    search_fields = ('title', 'description')
    list_editable = ('is_released',)

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity')

@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'theater', 'start_time', 'available_seats')
    list_filter = ('movie', 'theater')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'showtime', 'seats', 'booked_at')
    list_filter = ('showtime',)