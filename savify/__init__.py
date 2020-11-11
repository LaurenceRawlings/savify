"""
Savify

Download Spotify songs to mp3 with full metadata and cover art!

:Copyright: © 2020, Laurence Rawlings.
:License: MIT (see /LICENSE).
"""

from .savify import *
from .types import *

__title__ = 'Savify'
__author__ = """Laurence Rawlings"""
__email__ = 'contact@laurencerawlings.com'
__version__ = '2.0.7'
__license__ = 'MIT'
__docformat__ = 'restructuredtext en'

__all__ = ['savify', 'types']

def cli():
    from .cli import main
    main()
