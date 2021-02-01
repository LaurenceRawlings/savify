"""Console script for Savify."""
import sys
import re
import datetime
import click
import logging
from pathlib import Path

from . import __version__, __author__
from .types import *
from .utils import PathHolder, create_dir
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


class Choices:
    BOOL = ['True', 'False']
    PATH = '<SYSTEM PATH>'
    TYPE = ['track', 'album', 'playlist', 'artist']
    QUALITY = ['best', '320k', '256k', '192k', '128k', '96k', '32k', 'worst']
    FORMAT = ['mp3', 'aac', 'flac', 'm4a', 'opus', 'vorbis', 'wav']
    GROUPING = "%artist%, %album%, %playlist% separated by /"


def choices(choice):
    return ', '.join(choice)


def get_choice():
    return input('[INPUT]\tEnter choice: ').lower()


def show_banner():
    click.clear()
    click.echo(BANNER)


def validate_group(ctx, param, value):
    regex = r"^((%artist%|%album%|%playlist%)(\/(%artist%|%album%|%playlist%))*)+$"
    if re.search(regex, str(value)) or value is None:
        return value
    else:
        raise click.BadParameter('Group must be in the form x or x/x/x... where x in [%artist%, %album%, %playlist%]')


def guided_cli(type, quality, format, output, group, path, m3u, skip_cover_art):
    choice = ''
    options = ['0', '1', '2', '3', '4', '5', '6', '7', '8']
    errors = []
    while not choice or choice.lower() in options:
        show_banner()
        print('    Options\tChoices\t\t\t\t\t\tSelected\n--------------------------------------------------------'
              '----------------')
        print(f'[1] Type\t{choices(Choices.TYPE)}\t\t\t{type}\n'
              f'[2] Quality\t{choices(Choices.QUALITY)}\t{quality}\n'
              f'[3] Format\t{choices(Choices.FORMAT)}\t\t{format}\n'
              f'[4] Output\t{Choices.PATH}\t\t\t\t\t{output}\n'
              f'[5] Grouping\t{Choices.GROUPING}\t{group}\n'
              f'[6] Temp\t{Choices.PATH}\t\t\t\t\t{path}\n'
              f'[7] Create M3U\t{choices(Choices.BOOL)}\t\t\t\t\t{m3u}\n'
              f'[8] Cover-art\t{choices(Choices.BOOL)}\t\t\t\t\t{not skip_cover_art}\n\n'
              f'[0] Exit\n')
        for error in errors:
            print(f'[ERROR]\t{error}')
        errors = []
        choice = input('[INPUT]\tEnter an option or a search query: ')

        if choice == '0':
            sys.exit(0)
        elif choice == '1':
            type_input = get_choice()
            if type_input in Choices.TYPE:
                type = convert_type(type_input)
            else:
                errors.append('Invalid choice')
        elif choice == '2':
            quality_input = get_choice()
            if quality_input in Choices.QUALITY:
                quality = convert_quality(quality_input)
            else:
                errors.append('Invalid choice')
        elif choice == '3':
            format_input = get_choice()
            if format_input in Choices.FORMAT:
                format = convert_format(format_input)
            else:
                errors.append('Invalid choice')
        elif choice == '4':
            output_input = get_choice()
            try:
                create_dir(Path(output_input))
                output = output_input
            except:
                errors.append('Invalid path')
        elif choice == '5':
            group_input = get_choice()
            if validate_group(None, None, group_input):
                group = group_input
            else:
                errors.append('Invalid group syntax')
        elif choice == '6':
            path_input = get_choice()
            try:
                create_dir(Path(path_input))
                path = path_input
            except:
                errors.append('Invalid path')
        elif choice == '7':
            m3u_input = get_choice()
            if m3u_input in Choices.BOOL:
                m3u = convert_bool(m3u_input)
            else:
                errors.append('Invalid choice')
        elif choice == '8':
            skip_cover_art_input = get_choice()
            if skip_cover_art_input in Choices.BOOL:
                skip_cover_art = convert_bool(skip_cover_art_input)
            else:
                errors.append('Invalid choice')

    query = choice
    show_banner()
    return type, quality, format, output, group, path, m3u, query, not skip_cover_art


@click.command()
@click.help_option()
@click.version_option(version=__version__)
@click.option('-t', '--type', default=Choices.TYPE[0], help='Query type for text search.',
              type=click.Choice(Choices.TYPE))
@click.option('-q', '--quality', default=Choices.QUALITY[0], help='Bitrate for downloaded song(s).',
              type=click.Choice(Choices.QUALITY))
@click.option('-f', '--format', default=Choices.FORMAT[0], help='Format for downloaded song(s).',
              type=click.Choice(Choices.FORMAT))
@click.option('-g', '--group', default=None, callback=validate_group, help=Choices.GROUPING, type=click.STRING)
@click.option('-o', '--output', default=None, help='Output directory for downloaded song(s).',
              type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True, readable=True))
@click.option('-p', '--path', default=None, help='Path to directory to be used for data and temporary files.',
              type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True, readable=True))
@click.option('-m', '--m3u', is_flag=True, help='Create an M3U playlist file for your download.')
@click.option('--skip-cover-art', is_flag=True, help='Don\'t add cover art to downloaded song(s).')
@click.option('--silent', is_flag=True, help='Hide all output to stdout, overrides verbosity level.')
@click.option('-v', '--verbose', count=True, help='Change the log verbosity level. [-v, -vv]')
@click.argument('query', required=False)
def main(type, quality, format, output, group, path, m3u, verbose, silent, query, skip_cover_art, args=None):
    if not silent:
        show_banner()
        log_level = convert_log_level(verbose)
    else:
        log_level = None

    guided = False
    if not query:
        guided = True
        type, quality, format, output, group, path, m3u, query, skip_cover_art = \
            guided_cli(type, quality, format, output, group, path, m3u, skip_cover_art)

    path_holder = PathHolder(path, output)
    output_format = convert_format(format)
    query_type = convert_type(type)
    quality = convert_quality(quality)
    logger = Logger(path_holder.data_path, log_level)

    def setup(ffmpeg='ffmpeg'):
        return Savify(quality=quality, download_format=output_format, path_holder=path_holder, group=group,
                      skip_cover_art=skip_cover_art, logger=logger, ffmpeg_location=ffmpeg)

    def check_guided():
        if guided:
            input('\n[INFO]\tPress enter to exit...')

    try:
        s = setup()
    except FFmpegNotInstalledError as ex:
        from .ffmpegdl import FFmpegDL
        ffmpeg_dl = FFmpegDL(str(path_holder.data_path))

        if not ffmpeg_dl.check():
            logger.error(ex.message)
            if silent:
                check_guided()
                return 1

            choice = input('[INPUT]\tWould you like Savify to download FFmpeg for you? (Y/n) ')
            if choice.lower() == 'y' or not choice:
                logger.info('Downloading FFmpeg...')
                try:
                    ffmpeg_location = ffmpeg_dl.download()
                except:
                    logger.error('Failed to download FFmpeg!')
                    check_guided()
                    return 1
                logger.info(f'FFmpeg downloaded! [{ffmpeg_location}]')
            else:
                check_guided()
                return 1
        else:
            ffmpeg_location = ffmpeg_dl.final_location

        s = setup(ffmpeg=str(ffmpeg_location))
    except SpotifyApiCredentialsNotSetError as ex:
        logger.error(ex.message)
        check_guided()
        return 1

    try:
        s.download(query, query_type=query_type, create_m3u=m3u)
    except UrlNotSupportedError as ex:
        logger.error(ex.message)
        check_guided()
        return 1
    except InternetConnectionError as ex:
        logger.error(ex.message)
        check_guided()
        return 1

    check_guided()
    return 0


def convert_type(query_type):
    if query_type.lower() == 'track':
        return Type.TRACK
    elif query_type.lower() == 'album':
        return Type.ALBUM
    elif query_type.lower() == 'playlist':
        return Type.PLAYLIST
    elif query_type.lower() == 'artist':
        return Type.ARTIST


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


def convert_bool(boolean):
    return boolean.lower() == 'true'


def convert_log_level(verbosity: int):
    if verbosity == 1:
        return logging.WARNING
    elif verbosity == 2:
        return logging.DEBUG
    else:
        return logging.INFO


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
