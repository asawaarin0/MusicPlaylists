from django.db import models

# Create your models here.
class Playlist(models.Model):
    name = models.CharField(max_length = 100)
    date_created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Song(models.Model):
    name = models.CharField(max_length = 100)
    duration = models.DurationField()
    genre = models.CharField(max_length = 50)
    playlists = models.ManyToManyField(Playlist)
    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length = 100)
    songs = models.ManyToManyField(Song)
    def __str__(self):
        return self.name
    


