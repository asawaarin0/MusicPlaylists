from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_playlist, name="add playlist"),
    path("create_playlist/", views.create_playlist, name = "create playlist"),
    path("view_playlist/<int:playlist_id>/",  views.view_playlist, name = "view playlist"),
    path("delete_playlist/<int:playlist_id>/",  views.delete_playlist, name = "delete playlist"),
    path("add_song/<int:playlist_id>/",  views.add_song, name = "add song"),
    path("create_song/<int:playlist_id>/",  views.create_song, name = "create song"),
    path("delete_song/<int:song_id>/<int:playlist_id>/",  views.delete_song, name = "delete song"),
    path("edit_song/<int:song_id>/<int:playlist_id>/",  views.edit_song, name = "edit song"),
    path("update_song/<int:song_id>/<int:playlist_id>/",  views.update_song, name = "update song"),
    path("edit_playlist/<int:playlist_id>/",  views.edit_playlist, name = "edit playlist"),
    path("update_playlist/<int:playlist_id>/",  views.update_playlist, name = "update playlist")



]