import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from .track import Track
from .types import Type


class Spotify:
    def __init__(self, api_credentials=None):
        if api_credentials is None:
            self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        else:
            id, secret = api_credentials
            self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=id, client_secret=secret))

    def search(self, query, query_type=Type.TRACK):
        results = self.sp.search(q=query, limit=1, type=query_type)
        if len(results[query_type + 's']['items']) > 0:
            if query_type == Type.TRACK:
                return [Track(results[Type.TRACK + 's']['items'][0])]
            elif query_type == Type.ALBUM:
                return _pack_album(self.sp.album(results[Type.ALBUM + 's']['items'][0]['id']))
            elif query_type == Type.PLAYLIST:
                return self._get_playlist_tracks(results[Type.PLAYLIST + 's']['items'][0]['id'])
        else:
            return []


    def link(self, query):
        try:
            if '/track/' in query:
                return [Track(self.sp.track(query))]
            elif '/album/' in query:
                return _pack_album(self.sp.album(query))
            elif '/playlist/' in query:
                return self._get_playlist_tracks(query)
            else:
                return []
        except spotipy.exceptions.SpotifyException:
            return []


    def _get_playlist_tracks(self, playlist_id):
        playlist = self.sp.playlist(playlist_id)
        results = playlist['tracks']
        tracks = results['items']
        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])
        playlist['tracks'] = tracks
        return _pack_playlist(playlist)


def _pack_album(album):
    tracks = []
    for track in album['tracks']['items']:
        track_data = track
        track_data['album'] = album
        tracks.append(Track(track_data))
    return tracks


def _pack_playlist(playlist):
    tracks = []
    for track in playlist['tracks']:
        track_data = track['track']
        track_data['playlist'] = playlist['name']
        tracks.append(Track(track_data))
    return tracks    
