from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField()
    rating = models.CharField(max_length=5)
    synopsis = models.TextField(blank=True, null=True)
    director = models.CharField(max_length=100, blank=True, null=True)
    cast = models.TextField(blank=True, null=True,
                            help_text="Separate actor names with commas")
    genre = models.CharField(max_length=50, choices=[
        ('Action', 'Action'),
        ('Adventure', 'Adventure'),
        ('Animation', 'Animation'),
        ('Biography', 'Biography'),
        ('Drama', 'Drama'),
        ('Horror', 'Horror'),
        ('Thriller', 'Thriller'),
    ],
    default='Drama'
    )
    format = models.CharField(max_length=10, choices=[
        ('2D', '2D'),
        ('3D', '3D'),
    ],
    default='2D'
    )
    language = models.CharField(max_length=20, choices=[
        ('Chinese', 'Chinese'),
        ('English', 'English'),
        ('Hindi', 'Hindi'),
        ('Sinhala', 'Sinhala'),
        ('Tamil', 'Tamil'),
    ],
    default='English'
     )
    poster = models.ImageField(upload_to='media/', blank=True)
    is_released = models.BooleanField(default=False)
    release_date = models.DateField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.release_date and self.release_date <= timezone.now().date():
            self.is_released = True
        super().save(*args, **kwargs)

    def formatted_duration(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"

    def _str_(self):
        return self.title

class Theater(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    capacity = models.IntegerField()

    def _str_(self):
        return self.name

class SeatCategory(models.Model):
    name = models.CharField(max_length=50)
    price_2d = models.DecimalField(max_digits=6, decimal_places=2)
    price_3d = models.DecimalField(max_digits=6, decimal_places=2)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seat_categories')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)

    def get_price_for_format(self, format_type=None):
        if format_type:
            return self.price_3d if format_type == '3D' else self.price_2d
        return self.price_2d

    def __str__(self):
        return f"{self.name} (2D: Rs.{self.price_2d}, 3D: Rs.{self.price_3d})"

    def __str__(self):
        return f"{self.name} ({self.theater.name}) - 2D: Rs.{self.price_2d} | 3D: Rs.{self.price_3d}"

    class Meta:
        verbose_name_plural = "Seat Categories"

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    available_seats = models.IntegerField()

    @property
    def has_passed(self):
        return self.start_time <= timezone.now()

    @property
    def is_sold_out(self):
        return self.available_seats <= 0

    @property
    def is_available(self):
        return not self.has_passed and not self.is_sold_out

    def _str_(self):
        return f"{self.movie.title} at {self.theater.name}"

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings',null=True, blank=True)
    name = models.CharField(max_length=100, default='Guest User')
    email = models.EmailField(default='guest@example.com',
                              validators = [
                                  EmailValidator(
                                      message='Please enter a valid email address',
                                      code='invalid_email'
                                  ),
                              ]
    )
    phone = models.CharField(max_length=15,
                             default='0000000000',
                             validators =[
                                 RegexValidator(
                                     regex=r'^\d{10}$',
                                     message='Phone number must be 10 digits',
                                     code='invalid_phone'
                                 ),
                             ]
    )
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seat_category = models.ForeignKey(SeatCategory, on_delete=models.CASCADE, null=True, blank=True)
    seats = models.IntegerField(default=1)
    booked_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    format = models.CharField(max_length=10, choices=[
        ('2D', '2D'),
        ('3D', '3D'),
    ], default='2D')

    def save(self, *args, **kwargs):
        if not self.format and self.showtime:
            self.format = self.showtime.movie.format
        if self.seat_category:
            price = self.seat_category.price_2d if self.format == '2D' else self.seat_category.price_3d
            self.total_price = price * self.seats

        if hasattr(self, '_user') and self._user.is_authenticated:
            self.user = self._user
        super().save(*args, **kwargs)

    def __str__(self):
        category_name = self.seat_category.name if self.seat_category else "No Category"
        return f"{self.name} booked {self.seats} {category_name} seats for {self.showtime}"

    def __str__(self):
        user_type = self.user.username if self.user else "Guest"
        return f"{self.name} ({user_type}) booked {self.seats} {self.seat_category.name} seats for {self.showtime}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, validators=[
        RegexValidator(
            regex=r'^\d{10}$',
            message='Phone number must be 10 digits',
            code='invalid_phone'
        )
    ])
    full_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"


