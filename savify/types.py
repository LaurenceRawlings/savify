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
    Q32K = '32'
    Q96K = '96'
    Q128K = '128'
    Q192K = '192'
    Q256K = '256'
    Q320K =  '320'
    BEST = '0'
