class Track:
    def __init__(self, spotify_data):
        self._data = spotify_data

        try:
            self._album_name = spotify_data['album']['name']
        except KeyError:
            self._album_name = 'Unknown Album'
        try:
            self._release_date = spotify_data['album']['release_date']
        except KeyError:
            self._release_date = ''
        try:
            self._artists = spotify_data['artists']
        except KeyError:
            self._artists = [{'name': 'Unknown Artist'}]
        try:
            self._disc_number = spotify_data['disc_number']
        except KeyError:
            self._disc_number = ''
        try:
            self._url = spotify_data['external_urls']['spotify']
        except KeyError:
            self._url = ''
        try:
            self._id = spotify_data['id']
        except KeyError:
            from uuid import uuid1
            self._id = str(uuid1())
        try:
            self._name = spotify_data['name']
        except KeyError:
            self._name = 'Unknown Song'
        try:
            self._track_number = spotify_data['track_number']
        except KeyError:
            self._track_number = ''
        try:
            self._album_track_count = spotify_data['album']['total_tracks']
        except KeyError:
            self._album_track_count = ''
        try:
            self._uri = spotify_data['uri']
        except KeyError:
            self._uri = ''
        try:
            self._playlist = spotify_data['playlist']
        except KeyError:
            self._playlist = ''
        try:
            self._cover_art_url = spotify_data['album']['images'][0]['url']
        except (KeyError, IndexError):
            self._cover_art_url = 'https://developer.spotify.com/assets/branding-guidelines/icon3@2x.png'

    @property
    def album_name(self):
        return self._album_name

    @property
    def cover_art_url(self):
        return self._cover_art_url

    @property
    def release_date(self):
        return self._release_date

    @property
    def artist_names(self):
        try:
            return [artist['name'] for artist in self._artists]
        except KeyError:
            return ['Unknown Artist']

    @property
    def disc_number(self):
        return self._disc_number

    @property
    def url(self):
        return self._url

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def track_number(self):
        return self._track_number

    @property
    def album_track_count(self):
        return self._album_track_count

    @property
    def uri(self):
        return self._uri

    @property
    def playlist(self):
        return self._playlist

    def __repr__(self) -> str:
        return f'{self._id}\nName: {self._name}\nArtists: {self.artist_names}\nAlbum: {self._album_name}\n' \
               f'Release Date: {self._release_date}\nTrack: {self._track_number} / {self._album_track_count}\n' \
               f'Disc: {self._disc_number}\nCover Art: {self._cover_art_url}\nLink: {self._url}\nUri: {self._uri}'

    def __str__(self):
        return f'{self.artist_names[0]} - {self._name}'
