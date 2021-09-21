import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from .track import Track
from .types import Type


class Spotify:
    def __init__(self, api_credentials=None, language: str = None) -> None:
        if api_credentials is None:
            self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(), 
                language=language)
        else:
            client_id, client_secret = api_credentials
            self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
                client_id=client_id, client_secret=client_secret), language=language)

    def search(self, query, query_type=Type.TRACK, artist_albums: bool = False) -> list:
        results = self.sp.search(q=query, limit=1, type=query_type)
        if len(results[f'{query_type}s']['items']) > 0:
            if query_type == Type.TRACK:
                return [Track(results[f'{Type.TRACK}s']['items'][0])]

            elif query_type == Type.ALBUM:
                return _pack_album(self.sp.album(results[f'{Type.ALBUM}s']['items'][0]['id']))

            elif query_type == Type.PLAYLIST:
                return self._get_playlist_tracks(results[f'{Type.PLAYLIST}s']['items'][0]['id'])

            elif query_type == Type.ARTIST:
                if artist_albums:
                    albums = self._get_artist_albums(results[f'{Type.ARTIST}s']['items'][0]['id'])
                    tracks = list()
                    for album in albums:
                        tracks.extend(_pack_album(self.sp.album(album['id'])))

                    return tracks

                else:
                    return self._get_artist_top(results[f'{Type.ARTIST}s']['items'][0]['id'])

        else:
            return list()

    def link(self, query, artist_albums: bool = False) -> list:
        try:
            if 'track' in query:
                return [Track(self.sp.track(query))]

            elif 'album' in query:
                return _pack_album(self.sp.album(query))

            elif 'playlist' in query:
                return self._get_playlist_tracks(query)

            elif 'episode' in query:
                return [Track(self.sp.episode(query, 'US'), track_type=Type.EPISODE)]

            elif 'show' in query:
                return self._get_show_episodes(query)

            elif 'artist' in query:
                if artist_albums:
                    albums = self._get_artist_albums(query)
                    tracks = list()
                    for album in albums:
                        tracks.extend(_pack_album(self.sp.album(album['id'])))

                    return tracks

                else:
                    return self._get_artist_top(query)

            else:
                return list()
        except spotipy.exceptions.SpotifyException:
            return list()

    def _get_playlist_tracks(self, playlist_id) -> list:
        playlist = self.sp.playlist(playlist_id)
        results = playlist['tracks']
        tracks = results['items']
        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])

        playlist['tracks'] = tracks

        return _pack_playlist(playlist)

    def _get_show_episodes(self, show_id) -> list:
        show = self.sp.show(show_id, 'US')
        results = show['episodes']
        episodes = results['items']
        while results['next']:
            results = self.sp.next(results)
            episodes.extend(results['items'])

        show['episodes'] = episodes

        return _pack_show(show)

    def _get_artist_albums(self, artist_id):
        results = self.sp.artist_albums(artist_id, album_type='album')
        albums = results['items']
        while results['next']:
            results = self.sp.next(results)
            albums.extend(results['items'])

        results = self.sp.artist_albums(artist_id, album_type='single')
        albums.extend(results['items'])
        while results['next']:
            results = self.sp.next(results)
            albums.extend(results['items'])

        return albums

    def _get_artist_top(self, artist_id):
        tracks = list()
        for track in self.sp.artist_top_tracks(artist_id)['tracks']:
            tracks.append(Track(track))

        return tracks


def _pack_album(album) -> list:
    tracks = list()
    for track in album['tracks']['items']:
        track_data = track
        track_data['album'] = album
        tracks.append(Track(track_data))

    return tracks


def _pack_show(show) -> list:
    episodes = list()
    for episode in show['episodes']:
        episode_data = episode
        episode_data['show'] = show
        episodes.append(Track(episode_data, track_type=Type.EPISODE))

    return episodes


def _pack_playlist(playlist) -> list:
    tracks = list()
    for track in playlist['tracks']:
        if track is not None:
            track_data = track['track']
            if track_data is not None:
                track_data['playlist'] = f"{playlist['name']} - {playlist['owner']['display_name']}"
                tracks.append(Track(track_data))

    return tracks
