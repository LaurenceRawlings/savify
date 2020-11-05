class Track:
    def __init__(self, spotify_data):
        self._data = spotify_data

        self._album_name = spotify_data['album']['name']
        self._cover_art_url = spotify_data['album']['images'][0]['url']
        self._release_date = spotify_data['album']['release_date']
        self._artists = spotify_data['artists']
        self._disc_number = spotify_data['disc_number']
        self._url = spotify_data['external_urls']['spotify']
        self._id = spotify_data['id']
        self._name = spotify_data['name']
        self._track_number = spotify_data['track_number']
        self._album_track_count = spotify_data['album']['total_tracks']
        self._uri = spotify_data['uri']
        if 'playlist' in spotify_data:
            self._playlist = spotify_data['playlist']
        else:
            self._playlist = ''

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
        return [artist['name'] for artist in self._artists]

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
