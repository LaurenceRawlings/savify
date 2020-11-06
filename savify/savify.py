"""Main module for Savify."""

import time
from uuid import uuid1
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool

import validators
import tldextract
from youtube_dl import YoutubeDL
from ffmpy import FFmpeg

from . import utils
from .spotify import Spotify
from .types import Type, Platform, Format, Quality
from .track import Track
from .logger import Logger


def sort_dir(track, group):
    group = group.replace('%artist%', track.artist_names[0])
    group = group.replace('%album%', track.album_name)
    group = group.replace('%playlist%', track.playlist)

    return f'{group}'


class Savify:
    def __init__(self, api_credentials=None, quality=Quality.BEST, download_format=Format.MP3, output_path=utils.get_download_dir(), group=''):
        self.quality = quality
        self.download_format = download_format
        self.output_path = output_path
        self.group = group

        if api_credentials is None:
            if not(utils.check_env()):
                raise RuntimeError('Spotify API credentials not setup.')
            else:
                self.spotify = Spotify()
        else:
            self.spotify = Spotify(api_credentials=api_credentials)


    def parse_query(self, query, query_type=Type.TRACK):
        result = []

        if validators.url(query):
            domain = tldextract.extract(query).domain
            if domain == Platform.SPOTIFY:
                result = self.spotify.link(query)
            else:
                print('Invalid Spotify URL')
        else:
            if query_type == Type.TRACK:
                result = self.spotify.search(self.query, query_type=Type.TRACK)
            elif query_type == Type.ALBUM:
                result = self.spotify.search(self.query, query_type=Type.ALBUM)
            elif query_type == Type.PLAYLIST:
                result = self.spotify.search(self.query, query_type=Type.PLAYLIST)

        return result


    def download(self, query, query_type=Type.TRACK):
        if not(utils.check_ffmpeg()):
            print("FFmpeg must be installed to use Savify!")
            return

        queue = self.parse_query(query, query_type=query_type)

        if not(len(queue) > 0):
            print('No tracks found using the given query.')
            return

        start_time = time.time()
        with ThreadPool(cpu_count())as pool:
            jobs = pool.map(self._download, queue)

            failed_jobs = []
            for job in jobs:
                if job['returncode'] != 0:
                    failed_jobs.append(job)

        utils.clean(utils.get_temp_dir())

        message = (f'\nDownload Finished! \nCompleted {len(queue) - len(failed_jobs)}/{len(queue)} tracks in {time.time() - start_time:.4f}s')

        if len(failed_jobs) > 0:
            message += '\n\nFailed Tracks:\n'
            for failed_job in failed_jobs:
                message += f'\nTrack: {failed_job["track"].name}\nReason: {failed_job["error"]}\n'

        print(message)


    def _download(self, track: Track):
        logger = Logger()
        status = {
            'track': track,
            'returncode': -1
         }
        query = str(track) + ' (AUDIO)'
        output = self.output_path / f'{sort_dir(track, self.group)}' / f'{track.artist_names[0]} - {track.name}.{self.download_format}'

        if utils.check_file(output):
            print('Song already downloaded. Skipping...')
            status['returncode'] = 0
            return status

        utils.create_dir(output.parent)

        options = {
            'format': 'bestaudio/best',
            'outtmpl': f'{str(utils.get_temp_dir())}/{str(uuid1())}.%(ext)s',
            'restrictfilenames': True,
            'ignoreerrors': True,
            'nooverwrites': True,
            'noplaylist': True,
            'prefer_ffmpeg': True,
            'default_search': 'ytsearch',
            'logger': logger,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.download_format,
                'preferredquality': self.quality,
            }],
            'postprocessor_args': [
                '-write_id3v1', '1',
                '-id3v2_version', '3',
                '-q:a', '3',
                '-metadata', f'title={track.name}',
                '-metadata', f'album={track.album_name}',
                '-metadata', f'date={track.release_date}',
                '-metadata', f'artist={", ".join(track.artist_names)}',
                '-metadata', f'disc={track.disc_number}',
                '-metadata', f'track={track.track_number}/{track.album_track_count}',
            ],
        }

        if self.download_format == Format.MP3:
            options['postprocessor_args'].append('-codec:a')
            options['postprocessor_args'].append('libmp3lame')

        try:
            with YoutubeDL(options) as ydl:
                ydl.download([query])
        except:
            status['returncode'] = 1
            status['error'] = "Failed to download track."
            return status

        try:
            cover_art = utils.download_file(track.cover_art_url, extension='jpg')

            ffmpeg = FFmpeg(
                inputs={logger.final_destination: None, str(cover_art): None, },
                outputs={output: '-loglevel quiet -hide_banner -y -map 0:0 -map 1:0 -id3v2_version 3 '
                    '-metadata:s:v title="Album cover" -metadata:s:v comment="Cover (front)" '
                    # '-af "silenceremove=start_periods=1:start_duration=1:start_threshold=-60dB:'
                    # 'detection=peak,aformat=dblp,areverse,silenceremove=start_periods=1:'
                    # 'start_duration=1:start_threshold=-60dB:'
                    # 'detection=peak,aformat=dblp,areverse"'
                    }
            )

            ffmpeg.run()
        except:
            status['returncode'] = 2
            status['error'] = "Failed to add cover art."
            return status

        status['returncode'] = 0
        return status
