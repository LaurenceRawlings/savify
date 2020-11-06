======
Savify
======

.. image:: images/savify-banner.png
     :target: https://laurencerawlings.github.io/savify/
     :alt: Savify

.. image:: https://img.shields.io/pypi/v/savify.svg?style=for-the-badge
        :target: https://pypi.python.org/pypi/savify
        :alt: PyPi

.. image:: https://img.shields.io/travis/LaurenceRawlings/savify.svg?style=for-the-badge
        :target: https://travis-ci.org/github/LaurenceRawlings/savify
        :alt: Build

.. image:: https://img.shields.io/discord/701075588466737312?style=for-the-badge
     :target: https://discordapp.com/invite/SPuPEda
     :alt: Discord

.. image:: https://img.shields.io/github/stars/laurencerawlings/savify?style=for-the-badge
     :target: https://github.com/laurencerawlings/savify/stargazers
     :alt: Stars

.. image:: https://img.shields.io/github/contributors/laurencerawlings/savify?style=for-the-badge
     :target: https://github.com/laurencerawlings/savify/graphs/contributors
     :alt: Contributors

.. image:: https://img.shields.io/github/v/release/laurencerawlings/savify?include_prereleases&style=for-the-badge
     :target: https://github.com/laurencerawlings/savify/releases
     :alt: Release

.. image:: https://img.shields.io/github/downloads-pre/laurencerawlings/savify/latest/total?style=for-the-badge
     :target: https://github.com/laurencerawlings/savify/releases
     :alt: Downloads

.. image:: https://img.shields.io/readthedocs/savify?style=for-the-badge
     :target: https://savify.readthedocs.io
     :alt: Documentation Status

.. image:: https://pyup.io/repos/github/LaurenceRawlings/savify/shield.svg?style=for-the-badge
     :target: https://pyup.io/repos/github/LaurenceRawlings/savify/
     :alt: Updates


Savify
======

`Savify <https://laurencerawlings.github.io/savify/>`__ is a desktop
application that converts and downloads songs from Spotify, YouTube,
Soundcloud, Deezer and many other sites. Converting songs to MP3 with
quality as high as **320 kb/s**! The application will also scrape and
apply **id3V2 tags** to all of your songs. Tags include **title,
artists, year, album and even cover-art!**

Savify supports Spotify, YouTube, Soundcloud and Deezer playlists, with
an added **integrated search engine** function so if you don't have the
link you can simply search for the song name and artist and Savify will
download it!

As well as MP3, Savify can also download and convert to other file
types. Inside the application, you can specify which format and quality
you would like to download the song in for maximum compatibility across
all of your devices. Available formats: MP3, AAC, FLAC, M4A, OPUS,
VORBIS, and WAV. **NOTE: Tags and cover-art will only be applied to
songs downloaded in MP3 format.**

.. image:: images/donate.png
     :target: https://www.buymeacoffee.com/larry2k
     :alt: Donate

Download for Windows
====================

Download the latest release of Savify for Windows `here <https://github.com/LaurenceRawlings/savify/releases>`__

Windows Warning
---------------

| Running antivirus on your PC may interfere with Savify.
| To solve this please add an exception for Savify in your antivirus firewall.

FFMPEG
------

Savify relies on the open source FFMPEG library in order to convert and
apply meta data to the songs it downloads. Please make sure FFMPEG is
installed on your computer and added to the System PATH. Follow the
tutorial
`here <https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg>`__.

Playlists
=========

To avoid the issus of authentication in order to download your personal
playlists please make sure to set them to public. Otherwise Savify will
not be able to scrape the song data from them.

Installation
============

To use Savify you can either use one of the pre-packed releases (which I
recommend as you will not have to provide a Savify API key), or you can
download the source code and run the module directly using the CLI.

Download the latest release (recommended)
-----------------------------------------

Go `here <https://github.com/TechifyUK/savify/releases>`__ to download
the latest Savify.exe then make sure you have FFMPEG downloaded and it
added to your PATH as per the section above.

That's it, you should be good to go! See some usage examples below.

Using the Python module CLI
---------------------------

-  ``pip install -U savify``


Usage
=====

NOTE: Currently Savify only supports Spotify URLs and search queries,
however support for Spotify URIs will be added in the future.

Download Defaults:

-  type: track
-  quality: highest available
-  format: mp3
-  output: same directory as the Savify executable
-  group: no grouping

For more usage examples read the `docs <https://savify.readthedocs.io>`__.

Single track
------------

``savify.exe -s "https://open.spotify.com/playlist/4IaabtEqdYDkjiDK2o97HE?si=hMMondhaTVuYEoNNS9axLw"``

Playlist
--------

NOTE: The playlist you wish to download must be public for Savify to
find it.

``savify.exe -s "https://open.spotify.com/track/0PX9O7QzWYClP6PPuIaomj?si=DVNoVOs0RFevg_c_RwxLkQ"``

Album
-----

``savify.exe -s "https://open.spotify.com/album/4XJL9MdgCtvyCYpOotXO0s?si=I2yf_BKETQuFCyICawIbWA"``

Searching (no URL)
------------------

NOTE: The search query function will try to find the most relevant
result, however sometimes may return the wrong track. It is better to
use the URL of the Spotify track if you know it.

``savify.exe -s "Bru-C - You & I"``

For Developers
==============

If you want to try you hand at adding to Savify use the instructions
`here <CONTRIBUTING.rst>`__. From there you can make any additions you
think would make Savify better.

Spotify Application
-------------------

To develop and test a build of Savify you will need your own Spotify
developer application to access their API. To do this sign up
`here <https://developer.spotify.com/>`__. When you have make a new
application and take note of your client id and secret.

Now you need to add 2 environments variables to your system:

-  SPOTIPY\_CLIENT\_ID
-  SPOTIPY\_CLIENT\_SECRET

To find out how to do this find a tutorial online for your specific
operating system. Once you have done this make sure to restart your
shell.

Credits
=======

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
