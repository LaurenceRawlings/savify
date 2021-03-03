__all__ = ['Type', 'Platform', 'Format', 'Quality']


from enum import Enum


class Type(Enum):
    TRACK = 'track'
    ALBUM = 'album'
    PLAYLIST = 'playlist'
    EPISODE = 'episode'
    SHOW = 'show'
    ARTIST = 'artist'


class Platform(Enum):
    SPOTIFY = 'spotify'
    YOUTUBE = 'youtube'


class Format(Enum):
    MP3 = 'mp3'
    AAC = 'aac'
    FLAC = 'flac'
    M4A = 'm4a'
    OPUS = 'opus'
    VORBIS = 'vorbis'
    WAV = 'wav'


class Quality(Enum):
    WORST = '9'
    Q32K = '32'
    Q96K = '96'
    Q128K = '128'
    Q192K = '192'
    Q256K = '256'
    Q320K = '320'
    BEST = '0'
