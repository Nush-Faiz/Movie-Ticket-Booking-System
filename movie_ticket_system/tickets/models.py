from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField()  # in minutes
    rating = models.CharField(max_length=5)  # PG, R, etc.
    poster = models.ImageField(upload_to='posters/', blank=True)

    def _str_(self):
        return self.title

class Theater(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    capacity = models.IntegerField()

    def _str_(self):
        return self.name

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    available_seats = models.IntegerField()

    def _str_(self):
        return f"{self.movie.title} at {self.theater.name}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seats = models.IntegerField(default=1)
    booked_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.username} booked {self.showtime.movie.title}"


# Create your models here.
