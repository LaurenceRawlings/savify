#!/bin/sh

# This file defines all variables needed for bulk downloading with Docker
# Change the following settings, rename the file to "config.sh" 
# and run the script with bash bulk_download.sh

# Information: The docker image has to be previously built and tagged with savify[:dev]
# Use 'docker build -t savify:dev .' inside the project directory to build the Docker container
# Or use the Docker image provided in Docker Hub: laurencerawlings/savify:latest (recommended!)

# Specify download location, use pwd for current directory
LOCATION="`pwd`"
# Specify grouping schema
GROUPING="%artist%/%album%"

# Declare list with elements to download, use comment to stay organized!
declare -a ELEMENTS=(
          "https://open.spotify.com/playlist"  # Element name
          "https://open.spotify.com/album"     # Element name
)

# Set client ID and secret
CLIENT_ID=sampleid123
CLIENT_SECRET=samplesecret123

# Specify options used for downloading
# Recommendation: Use -m for auto-creating m3u playlist files
# and -a for downloading full artist albums
OPTIONS="-m -a"

# Specify the image you want Savify to run with
IMAGE_VERSION=laurencerawlings/savify:latest
