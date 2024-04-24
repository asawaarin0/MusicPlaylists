from django.contrib import admin
from .models import Playlist, Artist, Song

# Register your models here.
admin.site.register(Playlist)
admin.site.register(Artist)
admin.site.register(Song)