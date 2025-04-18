from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField()
    rating = models.CharField(max_length=5)
    genre = models.CharField(max_length=50, choices=[
        ('Action', 'Action'),
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


