from django.shortcuts import render, redirect
from .models import Movie, Showtime, Booking
from django.db.models import Q

def home(request):
    search_query = request.GET.get('search', '')
    genre = request.GET.get('genre')
    format = request.GET.get('format')
    language = request.GET.get('language')


    movies = Movie.objects.all()

    if search_query:
        movies = movies.filter(title__icontains=search_query)

    if genre and genre != "All":
        movies = movies.filter(genre=genre)
    if format and format != "All":
        movies = movies.filter(format=format)
    if language and language != "All":
        movies = movies.filter(language=language)

    context = {
        'movies': movies,
        'search_query': search_query,
        'selected_genre': genre or "All",
        'selected_format': format or "All",
        'selected_language': language or "All",
    }

    return render(request, 'tickets/home.html', {'movies': movies})


def movie_detail(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    showtimes = Showtime.objects.filter(movie=movie)
    return render(request, 'tickets/movie_details.html', {'movie': movie, 'showtimes': showtimes})


def book_ticket(request, showtime_id):
    showtime = Showtime.objects.get(id=showtime_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        seats = int(request.POST.get('seats', 1))

        if seats <= showtime.available_seats:
            Booking.objects.create(
                name=name,
                email=email,
                phone=phone,
                showtime=showtime,
                seats=seats
            )
            showtime.available_seats -= seats
            showtime.save()
            return redirect('booking_confirmation', booking_id=Booking.objects.latest('id').id)

    return render(request, 'tickets/book_ticket.html', {'showtime': showtime})

def booking_confirmation(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    return render(request, 'tickets/booking_confirmation.html', {'booking': booking})