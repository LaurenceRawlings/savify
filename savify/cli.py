"""Console script for Savify."""
import sys
import re
import click
import logging
from os import system
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
      \ $$$$/      https://github.com/LaurenceRawlings/savify   |  $$$$$$/
        \_/                                                      \______/ v{__version__}

"""

system('title Savify')


class Choices:
    BOOL = ['true', 'false']
    PATH = '<SYSTEM PATH>'
    TYPE = ['track', 'album', 'playlist', 'artist']
    QUALITY = ['best', '320k', '256k', '192k', '128k', '96k', '32k', 'worst']
    FORMAT = ['mp3', 'aac', 'flac', 'm4a', 'opus', 'vorbis', 'wav']
    GROUPING = "%artist%, %album%, %playlist% separated by /"


def choices(choice) -> str:
    return ', '.join(choice)


def get_choice() -> str:
    return input('[INPUT]\tEnter choice: ').lower()


def show_banner() -> None:
    click.clear()
    click.echo(BANNER)


def validate_group(_ctx, _param, value):
    regex = r"^((%artist%|%album%|%playlist%)(\/(%artist%|%album%|%playlist%))*)+$"
    if re.search(regex, str(value)) or value is None:
        return value
    else:
        raise click.BadParameter('Group must be in the form x or x/x/x... where x in [%artist%, %album%, %playlist%]')


def guided_cli(type, quality, format, output, group, path, m3u, artist_albums, skip_cover_art):
    choice = ''
    options = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
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
              f'[8] Cover-art\t{choices(Choices.BOOL)}\t\t\t\t\t{not skip_cover_art}\n'
              f'[9] All Albums\t{choices(Choices.BOOL)}\t\t\t\t\t{artist_albums}\n'
              f'\n[0] Exit\n')
        for error in errors:
            print(f'[ERROR]\t{error}')
        errors = []
        choice = input('[INPUT]\tEnter an option or a search query: ')

        # TODO: This is horrendous
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
                skip_cover_art = not convert_bool(skip_cover_art_input)
            else:
                errors.append('Invalid choice')
        elif choice == '9':
            artist_albums_input = get_choice()
            if artist_albums_input in Choices.BOOL:
                artist_albums = convert_bool(artist_albums_input)
            else:
                errors.append('Invalid choice')

    query = choice
    show_banner()
    return type, quality, format, output, group, path, m3u, query, artist_albums, skip_cover_art


@click.command(name='Savify', context_settings=dict(allow_extra_args=True, ignore_unknown_options=True))
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
@click.option('-a', '--artist-albums', is_flag=True, help='Download all artist songs and albums'
                                                          ', not just top 10 songs.')
@click.option('-l', '--language', default=None, help='ISO-639 language code to be used for searching and tags applying.',
              type=click.STRING)
@click.option('--skip-cover-art', is_flag=True, help='Don\'t add cover art to downloaded song(s).')
@click.option('--silent', is_flag=True, help='Hide all output to stdout, overrides verbosity level.')
@click.option('-v', '--verbose', count=True, help='Change the log verbosity level. [-v, -vv]')
@click.argument('query', required=False)
@click.pass_context
def main(ctx, type, quality, format, output, group, path, m3u, artist_albums, verbose, silent, query, skip_cover_art, language):
    if not silent:
        show_banner()
        log_level = convert_log_level(verbose)
    else:
        log_level = None

    guided = False
    if not query:
        guided = True
        type, quality, format, output, group, path, m3u, query, artist_albums, skip_cover_art = \
            guided_cli(type, quality, format, output, group, path, m3u, artist_albums, skip_cover_art)

    path_holder = PathHolder(path, output)
    output_format = convert_format(format)
    query_type = convert_type(type)
    quality = convert_quality(quality)
    logger = Logger(path_holder.data_path, log_level)
    ydl_options = {ctx.args[i][2:]: ctx.args[i+1] for i in range(0, len(ctx.args), 2)}

    def setup(ffmpeg='ffmpeg'):
        return Savify(quality=quality, download_format=output_format, path_holder=path_holder, group=group,
                      skip_cover_art=skip_cover_art, language=language, logger=logger, ffmpeg_location=ffmpeg, 
                      ydl_options=ydl_options)

    def check_guided():
        if guided:
            input('\n[INFO]\tPress enter to exit...')

    try:
        s = setup()
    except FFmpegNotInstalledError as ex:
        from .ffmpegdl import FFmpegDL
        ffmpeg_dl = FFmpegDL(str(path_holder.data_path))

        if not ffmpeg_dl.check_if_file():
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
        s.download(query, query_type=query_type, create_m3u=m3u, artist_albums=artist_albums)

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


def convert_type(query_type: str) -> Type:
    mapping = {
        'track': Type.TRACK,
        'album': Type.ALBUM,
        'playlist': Type.PLAYLIST,
        "artist": Type.ARTIST,
    }

    return mapping[query_type.lower()]


def convert_quality(quality: str) -> Quality:
    mapping = {
        'best': Quality.BEST,
        '320k': Quality.Q320K,
        '256k': Quality.Q256K,
        '192k': Quality.Q192K,
        '128k': Quality.Q128K,
        '98k': Quality.Q96K,
        '32k': Quality.Q32K,
        'worst': Quality.WORST,
    }

    return mapping[quality.lower()]


def convert_format(output_format: str) -> Format:
    mapping = {
        'mp3': Format.MP3,
        'aac': Format.AAC,
        'flac': Format.FLAC,
        'm4a': Format.M4A,
        'opus': Format.OPUS,
        'vorbis': Format.VORBIS,
        'wav': Format.WAV,
    }

    return mapping[output_format.lower()]


def convert_bool(boolean) -> bool:
    return boolean.lower() == 'true'


def convert_log_level(verbosity: int) -> int:
    if verbosity == 1:
        return logging.WARNING
    elif verbosity == 2:
        return logging.DEBUG
    else:
        return logging.INFO


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
