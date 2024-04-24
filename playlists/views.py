from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Playlist, Artist, Song
from datetime import timedelta
from pytz import timezone


# Create your views here.

def index(request):
    #display all the playlists of the user
    my_playlists = Playlist.objects.all()
    context = {"my_playlists":my_playlists}
    return render(request, "playlists/index.html", context)

def add_playlist(request):
    return render(request, "playlists/add_playlist.html")

def create_playlist(request):
    if request.method == 'POST':
        name = request.POST.get('playlist_name')
        if name:
            new_playlist = Playlist(name = name)
            new_playlist.save()
    return redirect('index')


def view_playlist(request, playlist_id):
    playlist = Playlist.objects.get(id = playlist_id)
    context = {"playlist":playlist}
    return render(request, "playlists/view_playlist.html", context)

def delete_playlist(request, playlist_id):
    playlist = Playlist.objects.get(id = playlist_id)
    playlist.delete()
    return redirect('index')


def add_song(request, playlist_id):
    context = {"playlist_id":playlist_id}
    return render(request, "playlists/add_song.html", context)

def create_song(request, playlist_id):
    if request.method == 'POST':
        song_name = request.POST.get("song_name")
        artists = request.POST.get("artists")
        genre = request.POST.get('genre')
        duration = request.POST.get('duration')
        hours, minutes, seconds = map(int, duration.split(':'))
        duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        artist_names = [artist.strip() for artist in artists.split(',')]
        playlist = Playlist.objects.get(pk=playlist_id)


        #check if song already exists
        existing_song = Song.objects.filter(name = song_name, genre = genre, duration=duration, artist__name__in = artist_names)
        if existing_song.exists():
            playlist.song_set.add(existing_song[0])
            playlist.save()
        else:
            #create the song
            #get or create artists
            artist_objects = [Artist.objects.get_or_create(name=name)[0] for name in artist_names]
            #create song and add it to playlist
            song = Song.objects.create(name = song_name, genre = genre, duration = duration)
            song.playlists.add(playlist)
            for artist in artist_objects:
                song.artist_set.add(artist)
            song.save()
        return redirect('view playlist', playlist_id=playlist_id)

def delete_song(request, song_id, playlist_id):
        song = Song.objects.get(pk=song_id)
        playlist = Playlist.objects.get(pk=playlist_id)
        song.playlists.remove(playlist)
        song.save()
        return redirect('view playlist', playlist_id=playlist_id)



def edit_song(request, song_id, playlist_id):
    song = Song.objects.get(pk=song_id)
    context={"song":song, "playlist_id":playlist_id}
    return render(request, "playlists/edit_song.html", context)

def update_song(request, song_id, playlist_id):
    if request.method == 'POST':
        #get updated details
        song_name = request.POST.get("song_name")
        artists = request.POST.get("artists")
        genre = request.POST.get('genre')
        duration = request.POST.get('duration')
        hours, minutes, seconds = map(int, duration.split(':'))
        duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)

        #get or create artists
        artist_names = [artist.strip() for artist in artists.split(',')]
        artist_objects = [Artist.objects.get_or_create(name=name)[0] for name in artist_names]

        #get song and update it
        song = Song.objects.get(pk=song_id)
        song.artist_set.clear()
        for artist in artist_objects:
            song.artist_set.add(artist)
        song.name = song_name
        song.genre = genre
        song.duration = duration
        song.save()
        return redirect('view playlist', playlist_id=playlist_id)

def edit_playlist(request, playlist_id):
    playlist = Playlist.objects.get(id = playlist_id)
    context = {"playlist":playlist}
    return render(request, "playlists/change_playlist.html", context)

def update_playlist(request, playlist_id):
    if request.method == 'POST':
        playlist = Playlist.objects.get(id = playlist_id)
        playlist.name = request.POST.get("name")
        playlist.save()
        return redirect('view playlist', playlist_id=playlist_id)



