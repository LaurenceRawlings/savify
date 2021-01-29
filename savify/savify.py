"""Main module for Savify."""

__all__ = ['Savify']

import time
import logging
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool
from pathlib import Path
from urllib.error import URLError

import validators
import tldextract
from youtube_dl import YoutubeDL
from ffmpy import FFmpeg, FFRuntimeError
from requests.exceptions import ConnectionError

from .utils import PathHolder, safe_path_string, check_env, check_ffmpeg, check_file, create_dir, clean
from .types import *
from .spotify import Spotify
from .track import Track
from .logger import Logger
from .exceptions import FFmpegNotInstalledError, SpotifyApiCredentialsNotSetError, UrlNotSupportedError, \
    YoutubeDlExtractionError, InternetConnectionError


def _sort_dir(track, group):
    if not group:
        return ''

    group = group.replace('%artist%', safe_path_string(track.artist_names[0]))
    group = group.replace('%album%', safe_path_string(track.album_name))
    group = group.replace('%playlist%', safe_path_string(track.playlist))

    return f'{group}'


def _progress(data):
    if data['status'] == 'downloading':
        pass
    elif data['status'] == 'finished':
        pass
    elif data['status'] == 'error':
        raise YoutubeDlExtractionError


class Savify:
    def __init__(self, api_credentials=None, quality=Quality.BEST, download_format=Format.MP3,
                 group=None, path_holder: PathHolder = None, retry: int = 3,
                 ydl_options: dict = {}, skip_cover_art: bool = False, logger: Logger = None,
                 ffmpeg_location: str = 'ffmpeg'):

        self.downloaded_cover_art = {}
        self.download_format = download_format
        self.path_holder = path_holder
        self.quality = quality
        self.group = group
        self.retry = retry
        self.ydl_options = ydl_options
        self.skip_cover_art = skip_cover_art
        self.ffmpeg_location = ffmpeg_location
        self.logger = logger

        if api_credentials is None:
            if not (check_env()):
                raise SpotifyApiCredentialsNotSetError
            else:
                self.spotify = Spotify()
        else:
            self.spotify = Spotify(api_credentials=api_credentials)

        if not check_ffmpeg() and self.ffmpeg_location == 'ffmpeg':
            raise FFmpegNotInstalledError

        clean(self.path_holder.get_temp_dir())

    def _parse_query(self, query, query_type=Type.TRACK) -> list:
        result = []

        if validators.url(query):
            domain = tldextract.extract(query).domain
            if domain == Platform.SPOTIFY:
                result = self.spotify.link(query)
            else:
                raise UrlNotSupportedError(query)
        else:
            if query_type == Type.TRACK:
                result = self.spotify.search(query, query_type=Type.TRACK)
            elif query_type == Type.ALBUM:
                result = self.spotify.search(query, query_type=Type.ALBUM)
            elif query_type == Type.PLAYLIST:
                result = self.spotify.search(query, query_type=Type.PLAYLIST)

        return result

    def download(self, query, query_type=Type.TRACK) -> None:
        try:
            queue = self._parse_query(query, query_type=query_type)
        except ConnectionError or URLError:
            raise InternetConnectionError

        if not (len(queue) > 0):
            self.logger.info('Nothing found using the given query.')
            return

        self.logger.info(f'Downloading {len(queue)} songs...')
        start_time = time.time()
        with ThreadPool(cpu_count())as pool:
            jobs = pool.map(self._download, queue)

            failed_jobs = []
            for job in jobs:
                if job['returncode'] != 0:
                    failed_jobs.append(job)

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

    def _download(self, track: Track) -> dict:
        status = {
            'track': track,
            'returncode': -1
        }

        extractor = 'ytsearch'
        query = f'{extractor}:{str(track)} audio'
        output = self.path_holder.get_download_dir() / f'{_sort_dir(track, self.group)}' / safe_path_string(
            f'{str(track)}.{self.download_format}')

        output_temp = f'{str(self.path_holder.get_temp_dir())}/{track.id}.%(ext)s'

        if check_file(output):
            self.logger.info(f'{str(track)} -> is already downloaded. Skipping...')
            status['returncode'] = 0
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
                '-metadata', f'artist={", ".join(track.artist_names)}',
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
        downloaded = False

        while not downloaded:
            attempt += 1

            try:
                with YoutubeDL(options) as ydl:
                    ydl.download([query])
                    if check_file(Path(output_temp)):
                        downloaded = True
            except YoutubeDlExtractionError as ex:
                if attempt > self.retry:
                    status['returncode'] = 1
                    status['error'] = "Failed to download song."
                    self.logger.error(ex.message)
                    return status

        from shutil import move, Error as ShutilError

        if self.download_format != Format.MP3 or self.skip_cover_art:
            try:
                move(output_temp, output)
            except ShutilError:
                status['returncode'] = 1
                status['error'] = 'Filesystem error.'
                self.logger.error('Failed to move temp file!')
                return status

            status['returncode'] = 0
            self.logger.info(f'Downloaded -> {str(track)}')
            return status

        attempt = 0
        added_artwork = False

        while not added_artwork:
            attempt += 1

            cover_art_name = f'{track.album_name} - {track.artist_names[0]}'

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
                added_artwork = True
            except FFRuntimeError:
                if attempt > self.retry:
                    try:
                        move(output_temp, output)
                        added_artwork = True
                    except ShutilError:
                        status['returncode'] = 1
                        status['error'] = 'Filesystem error.'
                        self.logger.error('Failed to move temp file!')
                        return status

        status['returncode'] = 0
        try:
            from os import remove
            remove(output_temp)
        except OSError:
            pass
        self.logger.info(f'Downloaded -> {str(track)}')
        return status
