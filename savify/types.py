__all__ = ['Type', 'Platform', 'Format', 'Quality']

class Type:
    TRACK = 'track'
    ALBUM = 'album'
    PLAYLIST = 'playlist'


class Platform:
    SPOTIFY = 'spotify'
    YOUTUBE = 'youtube'


class Format:
    MP3 = 'mp3'
    AAC = 'aac'
    FLAC = 'flac'
    M4A = 'm4a'
    OPUS = 'opus'
    VORBIS = 'vorbis'
    WAV = 'wav'


class Quality:
    WORST = '9'
    Q32K = '32K'
    Q96K = '96K'
    Q128K = '128K'
    Q192K = '192K'
    Q256K = '256K'
    Q320K =  '320K'
    BEST = '0'
