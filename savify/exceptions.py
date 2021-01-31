class SavifyError(Exception):
    def __init__(self, message='Savify ran into an error!'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class FFmpegNotInstalledError(SavifyError):
    def __init__(self, message='FFmpeg must be installed to use Savify! [https://ffmpeg.org/download.html]'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class SpotifyApiCredentialsNotSetError(SavifyError):
    def __init__(self, message='Spotify API credentials not setup! '
                               '[https://github.com/LaurenceRawlings/savify#spotify-application]'
                               '\n\tPlease go to https://developer.spotify.com/dashboard/applications '
                               'and create a new application,\n\tthen add your client id and secret to '
                               'your environment variables under SPOTIPY_ID and\n\tSPOTIPY_SECRET respectively. '
                               'Finally restart your command console.'
                 ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class UrlNotSupportedError(SavifyError):
    def __init__(self, url, message='URL not supported!'):
        self.url = url
        self.message = f'{message} [{self.url}]'
        super().__init__(self.message)

    def __str__(self):
        return self.message


class YoutubeDlExtractionError(SavifyError):
    def __init__(self, message='YoutubeDl failed to download the song!'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InternetConnectionError(SavifyError):
    def __init__(self, message='Connection timed out, check you have a stable internet connection!'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
