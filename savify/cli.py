"""Console script for Savify."""

import sys
import re
import datetime
import click
from pathlib import Path

from . import __version__, __author__
from .types import *
from .utils import get_download_dir
from .savify import Savify

BANNER = f"""

   ┎───────────┒      /$$$$$$                       /$$  /$$$$$$          
   ┃(((((((((((┃     /$$__  $$                     |__/ /$$__  $$         
   ┃(((((((((((┃    | $$  \__/  /$$$$$$  /$$    /$$ /$$| $$  \__//$$   /$$
   ┃(((((((((((┃    |  $$$$$$  |____  $$|  $$  /$$/| $$| $$$$   | $$  | $$
   ┃(((((((((((┃     \____  $$  /$$$$$$$ \  $$/$$/ | $$| $$_/   | $$  | $$
╭━━┛(((((((((((┗━━╮  /$$  \ $$ /$$__  $$  \  $$$/  | $$| $$     | $$  | $$
 ╲(((((((((((((((╱  |  $$$$$$/|  $$$$$$$   \  $/   | $$| $$     |  $$$$$$$
   ╲(((((((((((╱     \______/  \_______/    \_/    |__/|__/      \____  $$
     ╲(((((((╱                                                   /$$  | $$
       ╲(((╱                                                    |  $$$$$$/
         V                                                       \______/ v{__version__}
                 Copyright (c) 2018-{datetime.datetime.now().year} {__author__}

"""

def validate_group(ctx, param, value):
    regex = r"^((%artist%|%album%|%playlist%)(\/(%artist%|%album%|%playlist%))*)+$"
    if re.search(regex, str(value)) or value is None:
        return value
    else:
        raise click.BadParameter('Group must be in the form x or x/x/x... where x in [%artist%, %album%, %playlist%]')


@click.command()
@click.option('-t', '--type', default='track', help='Query type for text search', type=click.Choice(['track', 'album', 'playlist']))
@click.option('-q', '--quality', default='best', help='Bitrate for downloaded song(s)', type=click.Choice(['best', '320k', '256k', '192k', '128k', '96k', '32k', 'worst']))
@click.option('-f', '--format', default='mp3', help='Format for downloaded song(s)', type=click.Choice(['mp3', 'aac', 'flac', 'm4a', 'opus', 'vorbis', 'wav']))
@click.option('-o', '--output', default=str(get_download_dir()), help='Output directory for downloaded song(s)', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True, readable=True))
@click.option('-g', '--group', default=None, callback=validate_group, help='Directory grouping for downloaded song(s)', type=click.STRING)
@click.option('-q', '--quiet', is_flag=True, help='Hide Savify\'s output')
@click.argument('query')
def main(type, quality, format, output, group, quiet, query, args=None):
    click.clear()
    click.echo(BANNER)
    options = [type, quality, format, output, group]

    type = convert_type(type)
    quality = convert_quality(quality)
    format = convert_format(format)
    output = Path(output)

    s = Savify(quality=quality, download_format=format, output_path=output, group=group, quiet=quiet)
    s.download(query, query_type=type)

    return 0


def convert_type(type):
    if type.lower() == 'track':
        return Type.TRACK
    elif type.lower() == 'album':
        return Type.ALBUM
    elif type.lower() == 'playlist':
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


def convert_format(format):
    if format.lower() == 'mp3':
        return Format.MP3
    elif format.lower() == 'aac':
        return Format.AAC
    elif format.lower() == 'flac':
        return Format.FLAC
    elif format.lower() == 'M4A':
        return Format.M4A
    elif format.lower() == 'opus':
        return Format.OPUS
    elif format.lower() == 'vorbis':
        return Format.VORBIS
    elif format.lower() == 'wav':
        return Format.WAV


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
