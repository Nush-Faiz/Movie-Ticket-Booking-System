from django.db import models
from django.utils import timezone


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField()
    rating = models.CharField(max_length=5)
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
    default = '2D'
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
    price = models.DecimalField(max_digits=6, decimal_places=2)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seat_categories')

    def __str__(self):
        return f"{self.name} ({self.theater.name}) - ${self.price}"

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    available_seats = models.IntegerField()


    @property
    def is_available(self):
        return self.available_seats > 0 and self.start_time > timezone.now()

    def _str_(self):
        return f"{self.movie.title} at {self.theater.name}"

class Booking(models.Model):
    name = models.CharField(max_length=100, default='Guest User')
    email = models.EmailField(default='guest@example.com')
    phone = models.CharField(max_length=15, default='0000000000')
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seat_category = models.ForeignKey(SeatCategory, on_delete=models.CASCADE)
    seats = models.IntegerField(default=1)
    booked_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total_price = self.seat_category.price * self.seats
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} booked {self.seats} {self.seat_category.name} seats for {self.showtime}"


