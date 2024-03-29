======
Savify
======

.. image:: images/banner.png
     :alt: Savify

.. image:: https://img.shields.io/pypi/v/savify.svg?style=for-the-badge
     :target: https://pypi.python.org/pypi/savify
     :alt: PyPi

.. image:: https://img.shields.io/travis/LaurenceRawlings/savify.svg?style=for-the-badge
     :target: https://travis-ci.org/github/LaurenceRawlings/savify
     :alt: Build

.. image:: https://img.shields.io/readthedocs/savify?style=for-the-badge
     :target: https://savify.readthedocs.io
     :alt: Documentation Status

.. image:: https://img.shields.io/github/v/release/laurencerawlings/savify?include_prereleases&style=for-the-badge
     :target: https://github.com/laurencerawlings/savify/releases
     :alt: Release

.. image:: https://img.shields.io/github/downloads-pre/laurencerawlings/savify/latest/total?style=for-the-badge
     :target: https://github.com/laurencerawlings/savify/releases
     :alt: Downloads

.. image:: https://img.shields.io/discord/701075588466737312?style=for-the-badge
     :target: https://discordapp.com/invite/SPuPEda
     :alt: Discord

.. image:: https://img.shields.io/github/stars/laurencerawlings/savify?style=for-the-badge
     :target: https://github.com/laurencerawlings/savify/stargazers
     :alt: Stars

.. image:: https://img.shields.io/github/contributors/laurencerawlings/savify?style=for-the-badge
     :target: https://github.com/laurencerawlings/savify/graphs/contributors
     :alt: Contributors

.. image:: https://pyup.io/repos/github/LaurenceRawlings/savify/shield.svg?style=for-the-badge
     :target: https://pyup.io/repos/github/LaurenceRawlings/savify/
     :alt: Updates


`Savify <https://github.com/LaurenceRawlings/savify>`__ is a python
library that downloads songs from a selected provider (by default YouTube),
and then scrapes the meta information from Spotify. Given a query, Savify will find
and download songs to mp3 format with quality as high as **320 kb/s**!
The application will also scrape and write **id3v2 tags** to all your
songs. Tags include **title, artists, year, album and even cover-art!**

Savify supports all Spotify track, album, and playlist links. Additionally,
there is an **integrated search function** so even if you do not have the
Spotify link you can simply enter song name and Savify will download it!

As well as mp3, Savify can also download and convert to other file types.
Inside the application, you can specify which format and quality you would
like to download the song in for maximum compatibility across all your
devices. Available formats: mp3, aac, flac, m4a, opus, vorbis, and wav.
**Tags and cover art will only be applied to songs downloaded in mp3 format.**

Please note this library does not go against Spotify TOS in any way, songs
are not ripped directly from Spotify, but are instead downloaded from other
sources such as YouTube and Soundcloud using the youtube-dl python library.
Spotify is only used to gather accurate meta information to be embedded into
the downloaded song files.

**Visit our official Docker Hub image repository and get the latest Docker image: https://hub.docker.com/repository/docker/laurencerawlings/savify**

**Any questions or feedback join the** `Discord Server <https://discordapp.com/invite/SPuPEda>`__


.. image:: https://ko-fi.com/img/githubbutton_sm.svg
     :target: https://ko-fi.com/laurencerawlings
     :alt: Donate

FFmpeg
======

Savify relies on the open source FFmpeg library to convert and
write metadata to the songs it downloads. Please make sure FFmpeg is
installed on your computer and added to the System PATH. Follow the tutorial
`here <https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg>`__.

Playlists
=========

If you want to use Savify to download personal Spotify playlists, ensure their
visibility is set to 'Public'. This is so Savify can use the Spotify API to
retrieve the song details from your playlist.

Installation
============

If you are on Windows you can download the latest pre-packed executable
package (which I recommend as you will not have to provide a Savify API key),
or you can download the python library and run the module directly using the CLI.

Download the latest release
---------------------------

Go `here <https://github.com/LaurenceRawlings/savify/releases>`__ to download
the latest Savify.exe then make sure you have:

- FFmpeg downloaded and it added to your Path
- Spotify API credentials added to your environment variables

That is it, you should be good to go! See some usage examples below.

Using the Python module
-----------------------

``$ pip install -U savify``

Build Savify as Docker container
--------------------------------

Clone the repository and make sure you are in the root directory.
Execute the following build command:

``$ docker build -t savify:dev .``

Usage
=====

Currently Savify only supports Spotify URLs and search queries,
however support for Spotify URIs will be added in the future.

CLI
---

If you have downloaded the latest Savify.exe from the releases page
open your terminal and navigate to the same directory as the binary,
then you can run:

``$ Savify.exe``

If you are using the Python package and savify is installed to your
site-packages and your pip folder is in your PATH (which it should be
by default), from anywhere you can simply run:

``$ savify``

For help run:

``$ savify --help``

General usage
~~~~~~~~~~~~~

Using the default above:

``$ savify "https://open.spotify.com/track/4Dju9g4NCz0LDxwcjonSvI"``

Specifying your own options:

``$ savify "https://open.spotify.com/track/4Dju9g4NCz0LDxwcjonSvI" -q best -f mp3 -o "/path/to/downloads" -g "%artist%/%album%"``

With a search query:

``$ savify "You & I - Bru-C" -t track -q best -f mp3 -o "/path/to/downloads" -g "%artist%/%album%"``

Grouping
~~~~~~~~

Available variables: ``%artist%, %album%, %playlist%``

For example:

``$ savify "You & I - Bru-C" -o /path/to/downloads -g "%artist%/%album%"``

Would download in the following directory structure:

.. code-block:: python

     /path/to/downloads
          |
          |- /Bru-C
               |
               |- /Original Sounds
                    |
                    |- Bru-C - You & I.mp3

Download Defaults
-----------------

:Query Type: track
:Quality: best
:Format: mp3
:Path:
     Windows: HOME/AppData/Roaming/Savify/downloads

     Linux: HOME/.local/share/Savify/downloads

     MacOS: HOME/Library/Application Support/Savify/downloads
:Grouping: no grouping

For more usage examples read the `docs <https://savify.readthedocs.io>`__.

Docker
------

Run savify inside a container which can also be attached to other
container's networks. This is handy if you want to run multiple instances
of savify and/or want to use VPNs for downloading.
You can use your self-built Docker image or the official one. Make sure to
use the right Docker image name and tag.

``$ docker run laurencerawlings/savify:latest``

If no argument is specified, the container will print the help page. Simply
append your arguments, make sure you mount a folder from your host so
downloads are persistent (``-v``) - ``pwd`` is used to mount the current directory
you are in - and remove the container when done (``--rm``). You have to specify your
Spotify client ID and secret by using environment variables (``-e``):

.. code-block:: bash

    $ docker run --rm -v "`pwd`:/root/.local/share/Savify/downloads" \
               -e SPOTIPY_CLIENT_ID=client_id \
               -e SPOTIPY_CLIENT_SECRET=client_secret \
               laurencerawlings/savify:latest "https://open.spotify.com/playlist/..."

If you want to preserve your logs, you can mount the logging directory by simply
adding the following argument to the docker run command: ``-v "./logs:/root/.local/share/Savify/logs"``

Automate with a shell script:

``$ nano savify.sh``

.. code-block:: sh

    #!/bin/bash
    docker run --rm -v "`pwd`:/root/.local/share/Savify/downloads" \
               -e SPOTIPY_CLIENT_ID=client_id \
               -e SPOTIPY_CLIENT_SECRET=client_secret \
               laurencerawlings/savify:latest $1

Then run with:

``$ sh savify.sh "https://open.spotify.com/track/4Dju9g4NCz0LDxwcjonSvI"``

You also have the option to quickstart using our docker script which have an integrated VPN-check
to see if there are any VPN containers the script can connect to. The script is perfect for being
scheduled with cron:

.. code-block:: sh

    $ wget https://github.com/laurencerawlings/savify/latest/download/savify-docker-scripts.zip
    $ unzip savify-docker-scripts.zip && rm savify-docker-scripts.zip
    $ cd savify-docker-scripts/

You then have to edit the configuration file with your preferred text editor (we prefer nano),
save it (Ctrl + X, Y for saving changes in nano) and rename it to ``config.sh``.

.. code-block:: sh

    $ nano template.config.sh
    $ mv template.config.sh config.sh

You can then run the script:

.. code-block:: sh

    $ bash bulk-download.sh


Spotify Application
-------------------

To use the Savify Python module you will need your own Spotify
developer application to access their API. To do this sign up
`here <https://developer.spotify.com/>`__. When you have made a new
application take note of your client id and secret. You can pass
the id and secret to Savify in two ways:

Environment variables (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now you need to add 2 environment variables to your system:

``SPOTIPY_CLIENT_ID``

``SPOTIPY_CLIENT_SECRET``

To find out how to do this find a tutorial online for your specific
operating system. Once you have done this make sure to restart your
shell.

During object instantiation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can pass in your id and secret using a tuple when creating your
Savify object:

.. code-block:: python

     s = Savify(api_credentials=("CLIENT_ID","CLIENT_SECRET"))


Use in your Python project
--------------------------

Install the package to your environment:

``$ pip install savify``


Import and use Savify:

.. code-block:: python

     from savify import Savify
     from savify.types import Type, Format, Quality

     s = Savify()
     # Spotify URL
     s.download("SPOTIFY URL")

     # Search Query
     # Types: TRACK, ALBUM, PLAYLIST
     s.download("QUERY", query_type=Type.TRACK)

Savify optional constructor arguments (see above for defaults):

.. code-block:: python

    import logging

     from savify import Savify
     from savify.types import Type, Format, Quality
     from savify.utils import PathHolder

     # Quality Options: WORST, Q32K, Q96K, Q128K, Q192K, Q256K, Q320K, BEST
     # Format Options: MP3, AAC, FLAC, M4A, OPUS, VORBIS, WAV
     Savify(api_credentials=None, quality=Quality.BEST, download_format=Format.MP3, path_holder=PathHolder(downloads_path='path/for/downloads'), group='%artist%/%album%', quiet=False, skip_cover_art=False, log_level=logging.INFO)

Manually customising youtube-dl options:

.. code-block:: python

     from savify import Savify

     options = {
         'cookiefile': 'cookies.txt'
     }

     Savify(ydl_options=options)

Passing in your own logger:

.. code-block:: python

     from savify import Savify
     from savify.logger import Logger

     logger = Logger(log_location='path/for/logs', log_level=None) # Silent output

     Savify(logger=logger)

The group argument is used to sort you downloaded songs inside the
output path. Possible variables for the path string are: %artist%, %album%,
and %playlist%. The variables are replaced with the songs metadata.
For example, a song downloaded with the above Savify object would
save to a path like this:
`path/for/downloads/Example Artist/Example Album/Example Song.mp3`

For Developers
==============

If you want to try your hand at adding to Savify use the instructions
`here <CONTRIBUTING.rst>`__. From there you can make any additions you
think would make Savify better.

Tip
---

If you are developing Savify, install the pip package locally so you
can make and test your changes. From the root directory run:

``$ pip install -e .``

You can then run the Python module:

``$ savify``

Credits
=======

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
