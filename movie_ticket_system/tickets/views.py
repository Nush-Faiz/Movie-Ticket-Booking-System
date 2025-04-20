from django.shortcuts import render, redirect
from .models import Movie, Showtime, Booking, SeatCategory
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib import messages

def home(request):
    search_query = request.GET.get('search', '')
    genre = request.GET.get('genre')
    format = request.GET.get('format')
    language = request.GET.get('language')

    now_showing = Movie.objects.filter(is_released=True)
    upcoming = Movie.objects.filter(is_released=False).order_by('release_date')


    if search_query:
        now_showing = now_showing.filter(title__icontains=search_query)
        upcoming = upcoming.filter(title__icontains=search_query)

    if genre and genre != "All":
        now_showing = now_showing.filter(genre=genre)
        upcoming = upcoming.filter(genre=genre)

    if format and format != "All":
        now_showing = now_showing.filter(format=format)
        upcoming = upcoming.filter(format=format)

    if language and language != "All":
        now_showing = now_showing.filter(language=language)
        upcoming = upcoming.filter(language=language)


    context = {
        'now_showing': now_showing,
        'upcoming': upcoming,
        'search_query': search_query,
        'selected_genre': genre or "All",
        'selected_format': format or "All",
        'selected_language': language or "All",
    }

    return render(request, 'tickets/home.html', {'now_showing': now_showing, 'upcoming': upcoming })


def movie_detail(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    showtimes = Showtime.objects.filter(movie=movie)
    return render(request, 'tickets/movie_details.html', {'movie': movie, 'showtimes': showtimes})


def book_ticket(request, showtime_id):
    showtime = Showtime.objects.get(id=showtime_id)
    seat_categories = SeatCategory.objects.filter(theater=showtime.theater)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        seats = int(request.POST.get('seats', 1))
        seat_category_id = request.POST.get('seat_category')
        seat_category = SeatCategory.objects.get(id=seat_category_id)

        try:
            validate_email(email)

            booking = Booking(
                name=name,
                email=email,
                phone=phone,
                showtime=showtime,
                seat_category=seat_category,
                seats=seats
            )
            booking.full_clean()

            if seats <= showtime.available_seats:
                booking.save()
                showtime.available_seats -= seats
                showtime.save()
                return redirect('booking_confirmation', booking_id=booking.id)
            else:
                messages.error(request, 'Not enough available seats for this showtime.')

        except ValidationError as e:
            if hasattr(e, 'message') and 'email' in str(e.message):
                messages.error(request, 'Please enter a valid email address')
            elif hasattr(e, 'error_dict') and 'phone' in e.error_dict:
                messages.error(request, 'Phone number must be exactly 10 digits')
            else:
                messages.error(request, 'There was an error with your booking. Please check your information.')


    return render(request, 'tickets/book_ticket.html', {'showtime': showtime,'seat_categories': seat_categories})

def booking_confirmation(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    return render(request, 'tickets/booking_confirmation.html', {'booking': booking})