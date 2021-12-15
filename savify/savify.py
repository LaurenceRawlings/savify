"""Main module for Savify."""

__all__ = ['Savify']

import time
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool
from pathlib import Path
from shutil import move, Error as ShutilError
from urllib.error import URLError

import validators
import tldextract
import requests
from yt_dlp import YoutubeDL
from ffmpy import FFmpeg, FFRuntimeError

from .utils import PathHolder, safe_path_string, check_env, check_ffmpeg, check_file, create_dir, clean
from .types import *
from .spotify import Spotify
from .track import Track
from .logger import Logger
from .exceptions import FFmpegNotInstalledError, SpotifyApiCredentialsNotSetError, UrlNotSupportedError, \
    YoutubeDlExtractionError, InternetConnectionError


def _sort_dir(track: Track, group: str) -> str:
    if not group:
        return str()

    group = group.replace('%artist%', safe_path_string(track.artists[0]))
    group = group.replace('%album%', safe_path_string(track.album_name))
    group = group.replace('%playlist%', safe_path_string(track.playlist))

    return str(group)


def _progress(data) -> None:
    if data['status'] == 'downloading':
        pass
    elif data['status'] == 'finished':
        pass
    elif data['status'] == 'error':
        raise YoutubeDlExtractionError


class Savify:
    def __init__(self, api_credentials=None, quality=Quality.BEST, download_format=Format.MP3,
                 group=None, path_holder: PathHolder = None, retry: int = 3,
                 ydl_options: dict = None, skip_cover_art: bool = False, logger: Logger = None,
                 ffmpeg_location: str = 'ffmpeg') -> None:

        self.download_format = download_format
        self.ffmpeg_location = ffmpeg_location
        self.skip_cover_art = skip_cover_art
        self.downloaded_cover_art = dict()
        self.quality = quality
        self.queue_size = 0
        self.completed = 0
        self.retry = retry
        self.group = group

        # Config or defaults...
        self.ydl_options = ydl_options or dict()
        self.path_holder = path_holder or PathHolder()
        self.logger = logger or Logger(self.path_holder.data_path)

        if api_credentials is None:
            if not check_env():
                raise SpotifyApiCredentialsNotSetError

            self.spotify = Spotify()
        else:
            self.spotify = Spotify(api_credentials=api_credentials)

        if not check_ffmpeg() and self.ffmpeg_location == 'ffmpeg':
            raise FFmpegNotInstalledError

        clean(self.path_holder.get_temp_dir())
        self.check_for_updates()

    def check_for_updates(self) -> None:
        self.logger.info('Checking for updates...')
        latest_ver = requests.get('https://api.github.com/repos/LaurenceRawlings/savify/releases/latest').json()[
            'tag_name']

        from . import __version__
        current_ver = f'v{__version__}'

        if latest_ver == current_ver:
            self.logger.info('Savify is up to date!')
        else:
            self.logger.info('A new version of Savify is available, '
                             'get the latest release here: https://github.com/LaurenceRawlings/savify/releases')

    def _parse_query(self, query, query_type=Type.TRACK, artist_albums: bool = False) -> list:
        result = list()
        if validators.url(query) or query[:8] == 'spotify:':
            if tldextract.extract(query).domain == Platform.SPOTIFY:
                result = self.spotify.link(query, artist_albums=artist_albums)
            else:
                raise UrlNotSupportedError(query)

        else:
            if query_type == Type.TRACK:
                result = self.spotify.search(query, query_type=Type.TRACK)

            elif query_type == Type.ALBUM:
                result = self.spotify.search(query, query_type=Type.ALBUM)

            elif query_type == Type.PLAYLIST:
                result = self.spotify.search(query, query_type=Type.PLAYLIST)

            elif query_type == Type.ARTIST:
                result = self.spotify.search(query, query_type=Type.ARTIST, artist_albums=artist_albums)

        return result

    def download(self, query, query_type=Type.TRACK, create_m3u=False, artist_albums: bool = False) -> None:
        try:
            queue = self._parse_query(query, query_type=query_type, artist_albums=artist_albums)
            self.queue_size += len(queue)
        except requests.exceptions.ConnectionError or URLError:
            raise InternetConnectionError

        if not (len(queue) > 0):
            self.logger.info('Nothing found using the given query.')
            return

        self.logger.info(f'Downloading {len(queue)} songs...')
        start_time = time.time()
        with ThreadPool(cpu_count()) as pool:
            jobs = pool.map(self._download, queue)

        failed_jobs = list()
        successful_jobs = list()
        for job in jobs:
            if job['returncode'] != 0:
                failed_jobs.append(job)
            else:
                successful_jobs.append(job)

        if create_m3u and len(successful_jobs) > 0:
            track = successful_jobs[0]['track']
            playlist = safe_path_string(track.playlist)

            if not playlist:
                if query_type in {Type.EPISODE, Type.SHOW, Type.ALBUM}:
                    playlist = track.album_name
                elif query_type is Type.ARTIST:
                    playlist = track.artists[0]
                else:
                    playlist = track.name

            m3u = f'#EXTM3U\n#PLAYLIST:{playlist}\n'
            m3u_location = self.path_holder.get_download_dir() / f'{playlist}.m3u'

            for job in successful_jobs:
                track = job['track']
                location = job['location']
                m3u += f'#EXTINF:{str(queue.index(track))},{str(track)}\n'
                from os.path import relpath
                m3u += f'{relpath(location, m3u_location.parent)}\n'

            self.logger.info('Creating the M3U playlist file..')
            with open(m3u_location, 'w') as m3u_file:
                m3u_file.write(m3u)

        self.logger.info('Cleaning up...')
        clean(self.path_holder.get_temp_dir())

        message = f'Download Finished!\n\tCompleted {len(queue) - len(failed_jobs)}/{len(queue)}' \
                  f' songs in {time.time() - start_time:.0f}s\n'

        if len(failed_jobs) > 0:
            message += '\n\tFailed Tracks:\n'
            for failed_job in failed_jobs:
                message += f'\n\tSong:\t{str(failed_job["track"])}' \
                           f'\n\tReason:\t{failed_job["error"]}\n'

        self.logger.info(message)
        self.queue_size -= len(queue)
        self.completed -= len(queue)

    def _download(self, track: Track) -> dict:
        extractor = 'ytsearch'
        if track.platform == Platform.SPOTIFY:
            query = track.url if track.track_type == Type.EPISODE else f'{extractor}:{str(track)} audio'
        else:
            query = ''

        output = self.path_holder.get_download_dir() / f'{_sort_dir(track, self.group)}' / safe_path_string(
            f'{str(track)}.{self.download_format}')

        output_temp = f'{str(self.path_holder.get_temp_dir())}/{track.id}.%(ext)s'

        status = {
            'track': track,
            'returncode': -1,
            'location': output,
        }

        if check_file(output):
            self.logger.info(f'{str(track)} -> is already downloaded. Skipping...')
            status['returncode'] = 0
            self.completed += 1
            return status

        create_dir(output.parent)

        options = {
            'format': 'bestaudio/best',
            'outtmpl': output_temp,
            'restrictfilenames': True,
            'ignoreerrors': True,
            'nooverwrites': True,
            'noplaylist': True,
            'prefer_ffmpeg': True,
            'logger': self.logger,
            'progress_hooks': [_progress],

            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.download_format,
                'preferredquality': self.quality,
            }],

            'postprocessor_args': [
                '-write_id3v1', '1',
                '-id3v2_version', '3',
                '-metadata', f'title={track.name}',
                '-metadata', f'album={track.album_name}',
                '-metadata', f'date={track.release_date}',
                '-metadata', f'artist={"/".join(track.artists)}',
                '-metadata', f'disc={track.disc_number}',
                '-metadata', f'track={track.track_number}/{track.album_track_count}',
            ],

            **self.ydl_options,
        }

        output_temp = output_temp.replace('%(ext)s', self.download_format)

        if self.download_format == Format.MP3:
            options['postprocessor_args'].append('-codec:a')
            options['postprocessor_args'].append('libmp3lame')

        if self.ffmpeg_location != 'ffmpeg':
            options['ffmpeg_location'] = self.ffmpeg_location

        attempt = 0
        while True:
            attempt += 1

            try:
                with YoutubeDL(options) as ydl:
                    ydl.download([query])
                    if check_file(Path(output_temp)):
                        break

            except YoutubeDlExtractionError as ex:
                if attempt > self.retry:
                    status['returncode'] = 1
                    status['error'] = "Failed to download song."
                    self.logger.error(ex.message)
                    self.completed += 1
                    return status

        if self.download_format != Format.MP3 or self.skip_cover_art:
            try:
                move(output_temp, output)
            except ShutilError:
                status['returncode'] = 1
                status['error'] = 'Filesystem error.'
                self.logger.error('Failed to move temp file!')
                self.completed += 1
                return status

            status['returncode'] = 0
            self.completed += 1
            self.logger.info(f'Downloaded {self.completed} / {self.queue_size} -> {str(track)}')
            return status

        attempt = 0
        while True:
            attempt += 1
            cover_art_name = f'{track.album_name} - {track.artists[0]}'

            if cover_art_name in self.downloaded_cover_art:
                cover_art = self.downloaded_cover_art[cover_art_name]
            else:
                cover_art = self.path_holder.download_file(track.cover_art_url, extension='jpg')
                self.downloaded_cover_art[cover_art_name] = cover_art

            ffmpeg = FFmpeg(executable=self.ffmpeg_location,
                            inputs={str(output_temp): None, str(cover_art): None, },
                            outputs={
                                str(
                                    output): '-loglevel quiet -hide_banner -y -map 0:0 -map 1:0 -c copy -id3v2_version 3 '
                                             '-metadata:s:v title="Album cover" -metadata:s:v comment="Cover (front)" '
                                # '-af "silenceremove=start_periods=1:start_duration=1:start_threshold=-60dB:'
                                # 'detection=peak,aformat=dblp,areverse,silenceremove=start_periods=1:'
                                # 'start_duration=1:start_threshold=-60dB:'
                                # 'detection=peak,aformat=dblp,areverse"'
                            }
                            )

            try:
                ffmpeg.run()
                break

            except FFRuntimeError:
                if attempt > self.retry:
                    try:
                        move(output_temp, output)
                        break

                    except ShutilError:
                        status['returncode'] = 1
                        status['error'] = 'Filesystem error.'
                        self.logger.error('Failed to move temp file!')
                        self.completed += 1
                        return status

        status['returncode'] = 0
        try:
            from os import remove
            remove(output_temp)

        except OSError:
            pass

        self.completed += 1
        self.logger.info(f'Downloaded {self.completed} / {self.queue_size} -> {str(track)}')
        return status
