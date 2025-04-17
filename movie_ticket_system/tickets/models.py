from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField()
    rating = models.CharField(max_length=5)
    poster = models.ImageField(upload_to='media/', blank=True)

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
    name = models.CharField(max_length=100, default='Guest User')
    email = models.EmailField(default='guest@example.com')
    phone = models.CharField(max_length=15, default='0000000000')
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seats = models.IntegerField(default=1)
    booked_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.name} booked {self.showtime.movie.title}"


