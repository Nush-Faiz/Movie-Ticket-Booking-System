from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Showtime, Booking, SeatCategory, UserProfile
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
from .forms import ExtendedUserCreationForm, UserProfileForm, EditUsernameForm, EditEmailForm, EditFullNameForm, EditPhoneForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView,PasswordResetView, PasswordResetDoneView
from django.views.generic import TemplateView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User

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
        profile.save()

    form = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            new_username = form.cleaned_data['username']
            new_email = form.cleaned_data['email']
            if User.objects.exclude(pk=request.user.pk).filter(username=new_username).exists():
                messages.error(request, 'Username is already taken.')
            elif User.objects.exclude(pk=request.user.pk).filter(email=new_email).exists():
                messages.error(request, 'Email is already in use.')
            else:
                form.save()
                user = request.user
                user.username = new_username
                user.email = new_email
                user.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
        else:
            initial_data = {
                'email': request.user.email,
                'username': request.user.username,
                'full_name': profile.full_name if hasattr(profile, 'full_name') else '',
                'phone': profile.phone if hasattr(profile, 'phone') else ''
            }

            form = UserProfileForm(instance=profile, initial=initial_data)

    context = {
        'form': form,
        'profile': profile
    }

    return render(request, 'tickets/edit_profile.html', context)


@login_required
def edit_username(request):
    if request.method == 'POST':
        form = EditUsernameForm(request.POST, instance=request.user)
        if form.is_valid():
            new_username = form.cleaned_data['username']
            if User.objects.exclude(pk=request.user.pk).filter(username=new_username).exists():
                messages.error(request, 'Username is already taken.')
            else:
                form.save()
                messages.success(request, 'Username updated successfully!')
                return redirect('profile')
    else:
        form = EditUsernameForm(instance=request.user)

    return render(request, 'tickets/edit_field.html', {
        'form': form,
        'field_name': 'Username',
        'back_url': 'profile'
    })


@login_required
def edit_email(request):
    if request.method == 'POST':
        form = EditEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            new_email = form.cleaned_data['email']
            if User.objects.exclude(pk=request.user.pk).filter(email=new_email).exists():
                messages.error(request, 'Email is already in use.')
            else:
                form.save()
                messages.success(request, 'Email updated successfully!')
                return redirect('profile')
    else:
        form = EditEmailForm(instance=request.user)

    return render(request, 'tickets/edit_field.html', {
        'form': form,
        'field_name': 'Email',
        'back_url': 'profile'
    })


@login_required
def edit_full_name(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = EditFullNameForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Full name updated successfully!')
            return redirect('profile')
    else:
        form = EditFullNameForm(instance=profile)

    return render(request, 'tickets/edit_field.html', {
        'form': form,
        'field_name': 'Full Name',
        'back_url': 'profile'
    })


@login_required
def edit_phone(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = EditPhoneForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Phone number updated successfully!')
            return redirect('profile')
    else:
        form = EditPhoneForm(instance=profile)

    return render(request, 'tickets/edit_field.html', {
        'form': form,
        'field_name': 'Phone Number',
        'back_url': 'profile'
    })

@login_required
def user_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
    return render(request, 'tickets/profile.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'tickets/booking_detail.html', {'booking': booking})

@login_required
def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related(
        'showtime__movie',
        'showtime__theater',
        'seat_category'
    ).order_by('-booked_at')
    return render(request, 'tickets/my_bookings.html', {'bookings': bookings})

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
            user = request.user if request.user.is_authenticated else None
            try:
                user_profile = getattr(request.user, 'userprofile', None)
                name = request.POST.get('name', user_profile.full_name )
                email = request.POST.get('email', request.user.email )
                phone = request.POST.get('phone', user_profile.phone )
            except UserProfile.DoesNotExist:
                name = request.POST.get('name', request.user.username)
                email = request.POST.get('email', request.user.email)
                phone = request.POST.get('phone' ,request.user.phone)
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
                user=request.user if request.user.is_authenticated else None,
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

class CustomLogoutView(LogoutView):
    next_page = 'home'

def logout_confirm(request):
    return render(request, 'tickets/logout_confirm.html')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'tickets/password_reset.html'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        users = User.objects.filter(email=email)

        if users.exists():
            user = users.first()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            self.request.session['reset_token'] = f"{uid}/{token}"
            return super().form_valid(form)

        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'tickets/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.request.session.get('reset_token', '')
        context['reset_link'] = f"{self.request.build_absolute_uri('/')[:-1]}/reset/{token}"
        return context