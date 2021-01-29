#!/bin/sh

# This script will download the playlists you specified in parallel. 
# Remove the & at the bottom of the for loop, if you want the script to download them sequentially.
# When starting the script with bash download_playlists.sh, it will create n containers named 
# savify_(last 12 characters of the playlist link) so you can resolve which containers downloads which playlist.

# Information: The docker image has to be previously built and tagged with savify[:latest]
# Use 'docker build -t savify:latest .' inside the project directory to build the Docker container
# Or use the Docker image provided in Docker Hub

# Specify download location, use pwd for current directory
location="`pwd`"

# Declare list with playlists to download, use comment to stay organized!
declare -a playlists=(
          "https://open.spotify.com/playlist"  # Playlist 1 name
          "https://open.spotify.com/playlist"  # Playlist 2 name
)

# Set client ID and secret
client_id=sampleid123
client_secret=samplesecret123

for playlist in "${playlists[@]}";
do
(	echo "Downloading playlist: $playlist"
  id=${playlist: -12}
  docker run --rm -d --name "savify_${id//[^[:alnum:]]/}" \
		   -e SPOTIPY_CLIENT_ID=$client_id \
		   -e SPOTIPY_CLIENT_SECRET=$client_secret \
		   -v "$location":/download \
		   savify:latest \
		   "$playlist" -o /download -g "%playlist%" -q best -f mp3
) &
done
