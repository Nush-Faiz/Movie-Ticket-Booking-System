from django.shortcuts import render, redirect
from .models import Movie, Showtime, Booking

def home(request):
    movies = Movie.objects.all()
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