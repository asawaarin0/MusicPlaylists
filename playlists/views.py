from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Playlist, Artist, Song
from datetime import timedelta
from django.db import connection
# Create your views here

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


def create_playlist_report(request):
    return render(request, "playlists/create_report.html", {"my_playlists":Playlist.objects.all()})

def view_playlist_report(request):
    if request.method == 'POST':
        #execute prepared statement for given filtering criteria
        with connection.cursor() as cursor:
            cursor.execute("DROP VIEW IF EXISTS results")
            if request.POST.get("playlist").split(";")[0] == "All":
                 cursor.execute("""
                                CREATE VIEW results as
                                SELECT song.id as song_id, artist.id as artist_id, song.name as name, song.genre as Genre,  artist.name as artist_name, song.duration as Duration
                                FROM playlists_song_playlists as song_playlist
                                JOIN playlists_song as song on song.id = song_playlist.song_id
                                JOIN playlists_artist_songs as artist_songs on artist_songs.song_id = song.id
                                JOIN playlists_artist as artist on artist.id = artist_songs.artist_id
                                where genre = %s
                           """, [request.POST.get("genre")])
            else:
                cursor.execute("""
                                    CREATE VIEW results as
                                    SELECT song.id as song_id, artist.id as artist_id, song.name as name, song.genre as Genre,  artist.name as artist_name, song.duration as Duration
                                    FROM playlists_song_playlists as song_playlist
                                    JOIN playlists_song as song on song.id = song_playlist.song_id
                                    JOIN playlists_artist_songs as artist_songs on artist_songs.song_id = song.id
                                    JOIN playlists_artist as artist on artist.id = artist_songs.artist_id
                                    where song_playlist.playlist_id = %s AND genre = %s
                            """, [request.POST.get("playlist").split(";")[0], request.POST.get("genre")])
            cursor.execute("DROP VIEW IF EXISTS results_grouped")
            cursor.execute("CREATE VIEW results_grouped as SELECT name, Genre, TRIM(TRAILING ',' FROM GROUP_CONCAT(artist_name SEPARATOR ', ')) , Duration FROM results GROUP BY song_id")
            cursor.execute("SELECT * FROM results_grouped")
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append({
                    "name": row[0],
                    "genre":row[1],
                    "artists":row[2],
                    "duration": convert_microseconds_to_string(row[3])
                })
            #calculate number of songs returned
            cursor.execute("select count(DISTINCT song_id) from results")
            num_songs = cursor.fetchone()[0]
            #calculate most popular artists
            cursor.execute("""
                            SELECT artist_name
                            from results
                            group by artist_id
                            HAVING(
                                count(*) = (SELECT MAX(cnt) from (
                                    SELECT count(*) as cnt
                                    from results
                                    group by artist_id
                                ) as counts 
                           ))
                                """)
            most_popular_artists = []
            rows = cursor.fetchall()
            for row in rows:
                most_popular_artists.append(row[0])
            #calculate longest song
            cursor.execute("""  
                                select name, Duration
                                from results_grouped
                                where duration = (
                                    select MAX(Duration)
                                    from results_grouped
                                )
                                    """)
            rows = cursor.fetchall()
            longest_songs = []
            for row in rows:
                longest_songs.append({
                    "name":row[0],
                    "duration":convert_microseconds_to_string(row[1])
                })
            #calculate shortest song
            cursor.execute("""  
                                select name, Duration
                                from results_grouped
                                where duration = (
                                    select MIN(Duration)
                                    from results_grouped
                                )
                                    """)
            rows = cursor.fetchall()
            shortest_songs = []
            for row in rows:
                shortest_songs.append({
                    "name":row[0],
                    "duration":convert_microseconds_to_string(row[1])
                })
            context = {
                "playlist_name":request.POST.get("playlist").split(";")[1],
                "genre":request.POST.get("genre"),
                "results":result,
                "num_songs":num_songs,
                "most_popular_artists":most_popular_artists,
                "longest_songs":longest_songs,
                "shortest_songs":shortest_songs
            }
            return render(request, "playlists/view_report.html", context)



def convert_microseconds_to_string(microseconds):
    seconds = microseconds/1000000
    duration = timedelta(seconds=seconds)
    return str(duration)