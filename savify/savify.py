"""Main module for Savify."""

__all__ = ['Savify']

import time
import os
from uuid import uuid1
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool

import validators
import tldextract
from youtube_dl import YoutubeDL
from ffmpy import FFmpeg

from .utils import PathHolder, safe_path_string, check_env, check_ffmpeg, check_file, create_dir, clean
from .types import *
from .spotify import Spotify
from .track import Track
from .logger import Logger


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
        raise RuntimeError('youtube-dl download failed')


class Savify:
    def __init__(self, api_credentials=None, quality=Quality.BEST, download_format=Format.MP3,
                 group=None, quiet: bool = False, path_holder: PathHolder = None, retry: int = 3,
                 ydl_options: dict = {}, skip_cover_art: bool = False):

        self.downloaded_cover_art = {}
        self.download_format = download_format
        self.logger = Logger(quiet=quiet)
        self.path_holder = path_holder
        self.quality = quality
        self.group = group
        self.quiet = quiet
        self.retry = retry
        self.ydl_options = ydl_options
        self.skip_cover_art = skip_cover_art

        if api_credentials is None:
            if not (check_env()):
                raise RuntimeError('Spotify API credentials not setup.')
            else:
                self.spotify = Spotify()
        else:
            self.spotify = Spotify(api_credentials=api_credentials)

    def _parse_query(self, query, query_type=Type.TRACK) -> list:
        result = []

        if validators.url(query):
            domain = tldextract.extract(query).domain
            if domain == Platform.SPOTIFY:
                result = self.spotify.link(query)
            else:
                print('Invalid Spotify URL')
        else:
            if query_type == Type.TRACK:
                result = self.spotify.search(query, query_type=Type.TRACK)
            elif query_type == Type.ALBUM:
                result = self.spotify.search(query, query_type=Type.ALBUM)
            elif query_type == Type.PLAYLIST:
                result = self.spotify.search(query, query_type=Type.PLAYLIST)

        return result

    def download(self, query, query_type=Type.TRACK) -> None:
        if not (check_ffmpeg()):
            print("FFmpeg must be installed to use Savify!")
            return

        queue = self._parse_query(query, query_type=query_type)

        if not (len(queue) > 0):
            print('No tracks found using the given query.')
            return

        start_time = time.time()
        with ThreadPool(cpu_count())as pool:
            jobs = pool.map(self._download, queue)

            failed_jobs = []
            for job in jobs:
                if job['returncode'] != 0:
                    failed_jobs.append(job)

        clean(self.path_holder.get_temp_dir())

        message = f'\nDownload Finished! \nCompleted {len(queue) - len(failed_jobs)}/{len(queue)}' \
                  f' tracks in {time.time() - start_time:.4f}s '

        if len(failed_jobs) > 0:
            message += '\n\nFailed Tracks:\n'
            for failed_job in failed_jobs:
                message += f'\nTrack: {failed_job["track"].name}\nReason: {failed_job["error"]}\n'

        print(message)

    def _download(self, track: Track) -> dict:
        logger = Logger(quiet=self.quiet)
        status = {
            'track': track,
            'returncode': -1
        }

        query = str(track) + ' (AUDIO)'
        output = self.path_holder.get_download_dir() / f'{_sort_dir(track, self.group)}' / safe_path_string(
            f'{track.artist_names[0]} - {track.name}.{self.download_format}')

        output_temp = f'{str(self.path_holder.get_temp_dir())}/{str(uuid1())}.%(ext)s'

        if check_file(output):
            print('Song already downloaded. Skipping...')
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
            'default_search': 'ytsearch',
            'logger': logger,
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

        attempt = 0
        downloaded = False

        while not downloaded:
            attempt += 1

            try:
                with YoutubeDL(options) as ydl:
                    ydl.download([query])
                    downloaded = True

            except RuntimeError:
                if attempt > self.retry:
                    status['returncode'] = 1
                    status['error'] = "Failed to download track."
                    print(logger.log)
                    return status

        if self.download_format != Format.MP3 or self.skip_cover_art:
            try:
                import shutil
                shutil.move(output_temp, output)
            except RuntimeError:
                status['returncode'] = 1
                status['error'] = "Unknown."
                return status

            status['returncode'] = 0
            return status

        from ffmpy import FFRuntimeError

        attempt = 0
        added_artwork = False

        while not added_artwork:
            attempt += 1

            try:
                cover_art_name = f'{track.album_name} - {track.artist_names[0]}'

                if cover_art_name in self.downloaded_cover_art:
                    cover_art = self.downloaded_cover_art[cover_art_name]
                else:
                    cover_art = self.path_holder.download_file(track.cover_art_url, extension='jpg')
                    self.downloaded_cover_art[cover_art_name] = cover_art

                ffmpeg = FFmpeg(
                    inputs={output_temp: None, str(cover_art): None, },
                    outputs={output: '-loglevel quiet -hide_banner -y -map 0:0 -map 1:0 -c copy -id3v2_version 3 '
                                     '-metadata:s:v title="Album cover" -metadata:s:v comment="Cover (front)" '
                             # '-af "silenceremove=start_periods=1:start_duration=1:start_threshold=-60dB:'
                             # 'detection=peak,aformat=dblp,areverse,silenceremove=start_periods=1:'
                             # 'start_duration=1:start_threshold=-60dB:'
                             # 'detection=peak,aformat=dblp,areverse"'
                             }
                )

                ffmpeg.run()

                added_artwork = True

            except FFRuntimeError:
                if attempt > self.retry:
                    try:
                        import shutil
                        shutil.move(output_temp, output)
                        added_artwork = True
                    except RuntimeError:
                        status['returncode'] = 1
                        status['error'] = "Unknown."
                        return status

        status['returncode'] = 0
        return status
