from .types import Type, Platform


class Track:
    def __init__(self, spotify_data, track_type=Type.TRACK):
        self._data = spotify_data
        self.track_type = track_type
        self.platform = Platform.SPOTIFY

        try:
            self.album_name = spotify_data['album']['name']
        except KeyError:
            try:
                self.album_name = spotify_data['show']['name']
            except KeyError:
                if track_type == Type.EPISODE:
                    self.album_name = 'Unknown Show'
                else:
                    self.album_name = 'Unknown Album'
        try:
            self.release_date = spotify_data['album']['release_date']
        except KeyError:
            self.release_date = ''
        try:
            self.artists = _spotify_artist_names(spotify_data['artists'])
        except KeyError:
            try:
                self.artists = [spotify_data['show']['publisher']]
            except KeyError:
                if track_type == Type.EPISODE:
                    self.artists = ['Unknown Publisher']
                else:
                    self.artists = ['Unknown Artist']
        try:
            self.disc_number = spotify_data['disc_number']
        except KeyError:
            self.disc_number = ''
        try:
            self.url = spotify_data['external_urls']['spotify']
        except KeyError:
            self.url = ''
        try:
            self.id = spotify_data['id']
        except KeyError:
            from uuid import uuid1
            self.id = str(uuid1())
        try:
            self.name = spotify_data['name']
        except KeyError:
            if track_type == Type.EPISODE:
                self.name = 'Unknown Episode'
            else:
                self.name = 'Unknown Song'
        try:
            self.track_number = spotify_data['track_number']
        except KeyError:
            self.track_number = ''
        try:
            self.album_track_count = spotify_data['album']['total_tracks']
        except KeyError:
            self.album_track_count = ''
        try:
            self.uri = spotify_data['uri']
        except KeyError:
            self.uri = ''
        try:
            self.playlist = spotify_data['playlist']
        except KeyError:
            self.playlist = ''
        try:
            self.cover_art_url = spotify_data['album']['images'][0]['url']
        except (KeyError, IndexError):
            try:
                self.cover_art_url = spotify_data['images'][0]['url']
            except (KeyError, IndexError):
                self.cover_art_url = 'https://developer.spotify.com/assets/branding-guidelines/icon3@2x.png'

    def __repr__(self) -> str:
        return f'{self.id}\nName: {self.name}\nArtists: {self.artists}\nAlbum: {self.album_name}\n' \
               f'Release Date: {self.release_date}\nTrack: {self.track_number} / {self.album_track_count}\n' \
               f'Disc: {self.disc_number}\nCover Art: {self.cover_art_url}\nLink: {self.url}\nUri: {self.uri}'

    def __str__(self):
        return f'{self.artists[0]} - {self.name}'


def _spotify_artist_names(artist_data):
    try:
        return [artist['name'] for artist in artist_data]
    except KeyError:
        return ['Unknown Artist']
