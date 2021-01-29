"""Console script for Savify."""
import sys
import re
import datetime
import click
import logging

from . import __version__, __author__
from .types import *
from .utils import PathHolder
from .savify import Savify
from .logger import Logger
from .exceptions import FFmpegNotInstalledError, SpotifyApiCredentialsNotSetError, UrlNotSupportedError, \
    InternetConnectionError

BANNER = rf"""

  /$$$$$$$$$$$$$      /$$$$$$                       /$$  /$$$$$$
 | $$$$$$$$$$$$$     /$$__  $$                     |__/ /$$__  $$
 | $$$$$$$$$$$$$    | $$  \__/  /$$$$$$  /$$    /$$ /$$| $$  \__//$$   /$$
 | $$$$$$$$$$$$$    |  $$$$$$  |____  $$|  $$  /$$/| $$| $$$$   | $$  | $$
 | $$$$$$$$$$$$$     \____  $$  /$$$$$$$ \  $$/$$/ | $$| $$_/   | $$  | $$
/$$$$$$$$$$$$$$$$$$  /$$  \ $$ /$$__  $$  \  $$$/  | $$| $$     | $$  | $$
\ $$$$$$$$$$$$$$$$/ |  $$$$$$/|  $$$$$$$   \  $/   | $$| $$     |  $$$$$$$
  \ $$$$$$$$$$$$/    \______/  \_______/    \_/    |__/|__/      \____  $$
    \ $$$$$$$$/                                                  /$$  | $$
      \ $$$$/                                                   |  $$$$$$/
        \_/                                                      \______/ v{__version__}
                 Copyright (c) 2018-{datetime.datetime.now().year} {__author__}

"""


def validate_group(ctx, param, value):
    regex = r"^((%artist%|%album%|%playlist%)(\/(%artist%|%album%|%playlist%))*)+$"
    if re.search(regex, str(value)) or value is None:
        return value
    else:
        raise click.BadParameter('Group must be in the form x or x/x/x... where x in [%artist%, %album%, %playlist%]')


@click.command()
@click.help_option()
@click.version_option(version=__version__)
@click.option('-t', '--type', default='track', help='Query type for text search.',
              type=click.Choice(['track', 'album', 'playlist']))
@click.option('-q', '--quality', default='best', help='Bitrate for downloaded song(s).',
              type=click.Choice(['best', '320k', '256k', '192k', '128k', '96k', '32k', 'worst']))
@click.option('-f', '--format', default='mp3', help='Format for downloaded song(s).',
              type=click.Choice(['mp3', 'aac', 'flac', 'm4a', 'opus', 'vorbis', 'wav']))
@click.option('-g', '--group', default=None, callback=validate_group, help='Directory grouping for downloaded song(s).',
              type=click.STRING)
@click.option('-o', '--output', default=None, help='Output directory for downloaded song(s).',
              type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True, readable=True))
@click.option('-p', '--path', default=None, help='Path to directory to be used for data and temporary files.',
              type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True, readable=True))
@click.option('--skip-cover-art', is_flag=True, help='Don\'t add cover art to downloaded song(s).')
@click.option('--silent', is_flag=True, help='Hide all output to stdout, overrides verbosity level.')
@click.option('-v', '--verbose', count=True, help='Change the log verbosity level. [-v, -vv]')
@click.argument('query')
def main(type, quality, format, output, group, path, verbose, silent, query, skip_cover_art, args=None):
    if not silent:
        click.clear()
        click.echo(BANNER)
        log_level = convert_log_level(verbose)
    else:
        log_level = None

    path_holder = PathHolder(path, output)
    output_format = convert_format(format)
    query_type = convert_type(type)
    quality = convert_quality(quality)
    logger = Logger(path_holder.data_path, log_level)

    def setup(ffmpeg='ffmpeg'):
        return Savify(quality=quality, download_format=output_format, path_holder=path_holder, group=group,
                      skip_cover_art=skip_cover_art, logger=logger, ffmpeg_location=ffmpeg)

    try:
        s = setup()
    except FFmpegNotInstalledError as ex:
        from .ffmpegdl import FFmpegDL
        ffmpeg_dl = FFmpegDL(str(path_holder.data_path))

        if not ffmpeg_dl.check():
            logging.error(ex.message)
            if silent:
                return 1

            choice = input('[INPUT]\tWould you like Savify to download FFmpeg for you? (Y/n) ')
            if choice.lower() == 'y' or not choice:
                logging.info('Downloading FFmpeg...')
                try:
                    ffmpeg_location = ffmpeg_dl.download()
                except:
                    logging.error('Failed to download FFmpeg!')
                    return 1
                logging.info(f'FFmpeg downloaded! [{ffmpeg_location}]')
            else:
                return 1
        else:
            ffmpeg_location = ffmpeg_dl.final_location

        s = setup(ffmpeg=str(ffmpeg_location))
    except SpotifyApiCredentialsNotSetError as ex:
        logging.error(ex.message)
        return 1

    try:
        s.download(query, query_type=query_type)
    except UrlNotSupportedError as ex:
        logging.error(ex.message)
        return 1
    except InternetConnectionError as ex:
        logging.error(ex.message)
        return 1

    return 0


def convert_type(query_type):
    if query_type.lower() == 'track':
        return Type.TRACK
    elif query_type.lower() == 'album':
        return Type.ALBUM
    elif query_type.lower() == 'playlist':
        return Type.PLAYLIST


def convert_quality(quality):
    if quality.lower() == 'best':
        return Quality.BEST
    elif quality.lower() == '320k':
        return Quality.Q320K
    elif quality.lower() == '256k':
        return Quality.Q256K
    elif quality.lower() == '192k':
        return Quality.Q192K
    elif quality.lower() == '128k':
        return Quality.Q128K
    elif quality.lower() == '96k':
        return Quality.Q96K
    elif quality.lower() == '32k':
        return Quality.Q32K
    elif quality.lower() == 'worst':
        return Quality.WORST


def convert_format(output_format):
    if output_format.lower() == 'mp3':
        return Format.MP3
    elif output_format.lower() == 'aac':
        return Format.AAC
    elif output_format.lower() == 'flac':
        return Format.FLAC
    elif output_format.lower() == 'M4A':
        return Format.M4A
    elif output_format.lower() == 'opus':
        return Format.OPUS
    elif output_format.lower() == 'vorbis':
        return Format.VORBIS
    elif output_format.lower() == 'wav':
        return Format.WAV


def convert_log_level(verbosity: int):
    if verbosity == 1:
        return logging.WARNING
    elif verbosity == 2:
        return logging.DEBUG
    else:
        return logging.INFO


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
