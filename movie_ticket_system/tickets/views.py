from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Showtime, Booking, SeatCategory
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .forms import ExtendedUserCreationForm
from .forms import UserProfileForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required

import logging
logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        logger.debug(f"Form data: {request.POST}")
        if form.is_valid():
            logger.debug("Form is valid")
            user = form.save()
            logger.debug(f"User created: {user}")
            profile = user.userprofile
            profile.full_name = form.cleaned_data['full_name']
            profile.phone = form.cleaned_data['phone']
            profile.save()

            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            logger.debug(f"Form errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ExtendedUserCreationForm()
    return render(request, 'tickets/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'tickets/login.html')


@login_required
def edit_profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'tickets/edit_profile.html', {'form': form})

def home(request):
    search_query = request.GET.get('search', '')
    genre = request.GET.get('genre')
    format = request.GET.get('format')
    language = request.GET.get('language')

    featured_movies = Movie.objects.filter(is_featured=True)[:3]
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
        'selected_genre': genre or "ALL",
        'selected_format': format or "ALL",
        'selected_language': language or "ALL",
        'featured_movies': featured_movies,
    }

    return render(request, 'tickets/home.html', {'now_showing': now_showing, 'upcoming': upcoming,'featured_movies': featured_movies })


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    today = timezone.now().date()

    date_range = [today + timedelta(days=i) for i in range(7)]

    selected_date_str = request.GET.get('date')
    selected_date = today

    if selected_date_str:
        try:
            selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except:
            selected_date = today

    showtimes = Showtime.objects.filter(
        movie=movie,
        start_time__date=selected_date
    ).order_by('start_time').select_related('theater')

    theaters_data = []
    theaters = {showtime.theater for showtime in showtimes}

    for theater in theaters:
        categories = SeatCategory.objects.filter(
            theater=theater
        ).filter(
            Q(movie=movie) | Q(movie__isnull=True)
        )

        theater_showtimes = showtimes.filter(theater=theater)

        theaters_data.append({
            'theater': theater,
            'categories': categories,
            'showtimes': theater_showtimes
        })

        for category in categories:
            category.price = category.get_price_for_format(movie.format)

    context = {
        'movie': movie,
        'date_range': date_range,
        'today': today,
        'theaters_data': theaters_data,
        'selected_date': selected_date,
    }
    return render(request, 'tickets/movie_details.html', context)


def book_ticket(request, showtime_id):
    showtime = Showtime.objects.get(id=showtime_id)
    seat_categories = SeatCategory.objects.filter(
        Q(theater=showtime.theater) &
        (Q(movie=showtime.movie) | Q(movie__isnull=True)))

    for category in seat_categories:
        category.price = category.get_price_for_format(showtime.movie.format)

    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                profile = request.user.userprofile
                name = request.POST.get('name', profile.full_name)
                email = request.POST.get('email', request.user.email)
                phone = request.POST.get('phone', profile.phone)
            except UserProfile.DoesNotExist:
                name = request.POST.get('name', request.user.username)
                email = request.POST.get('email', request.user.email)
                phone = request.POST.get('phone')
        else:
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
                seats=seats,
                format = showtime.movie.format
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


    return render(request, 'tickets/book_ticket.html', {'showtime': showtime,'seat_categories': seat_categories,'movie_format': showtime.movie.format, 'user': request.user})

def booking_confirmation(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    return render(request, 'tickets/booking_confirmation.html', {'booking': booking})

def upcoming_movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'tickets/upcoming_movie_detail.html', {'movie': movie})

def about_us(request):
    return render(request, 'tickets/about_us.html')

def faqs(request):
    return render(request, 'tickets/faqs.html')

def feedback(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"""
                You have received a new feedback message:

                From: {name} <{email}>
                Subject: {subject}

                Message:
                {message}
                """
        try:

            send_mail(
                subject=f'Feedback: {subject}',
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )


            send_mail(
                subject='Thank you for your feedback',
                message=f'Hello {name},\n\nWe have received your feedback and will get back to you soon.\n\nYour message:\n{message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, 'Thank you for your feedback! We will get back to you soon.')
            return redirect('feedback')

        except Exception as e:
            messages.error(request, f'There was an error sending your feedback. Please try again later. Error: {str(e)}')

    return render(request, 'tickets/feedback.html')


def user_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
    return render(request, 'tickets/profile.html', {'bookings': bookings})