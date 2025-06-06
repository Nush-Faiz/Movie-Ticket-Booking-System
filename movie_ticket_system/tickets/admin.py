from django.contrib import admin
from .models import Movie, Theater, Showtime, Booking,SeatCategory

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_released', 'release_date', 'director', 'genre', 'rating')
    list_filter = ('is_released', 'genre', 'rating', 'release_date')
    search_fields = ('title', 'description','synopsis', 'director', 'cast')
    list_editable = ('is_released',)
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'synopsis')
        }),
        ('Details', {
            'fields': ('director', 'cast', 'duration', 'rating', 'genre',
                       'format', 'language', 'poster', 'release_date', 'is_released')
        }),
    )

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity')

@admin.register(SeatCategory)
class SeatCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'theater', 'price_2d', 'price_3d','movie')
    list_filter = ('theater','movie')
    search_fields = ('name', 'theater__name')
    fieldsets = (
        (None, {
            'fields': ('name', 'theater', 'movie')
        }),
        ('Pricing', {
            'fields': ('price_2d', 'price_3d')
        }),
    )

@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'theater', 'start_time', 'available_seats')
    list_filter = ('movie', 'theater')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'showtime', 'get_seat_category', 'seats', 'total_price', 'booked_at')
    list_filter = ('showtime', 'seat_category')

    def get_seat_category(self, obj):
        return obj.seat_category.name if obj.seat_category else "No Category"
    get_seat_category.short_description = 'Seat Category'