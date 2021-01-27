#!/bin/sh

# Information: The docker image has to be previously built and tagged with savify[:latest]
# Use 'docker build -t savify .' inside the project directory to build the Docker container

# Specify download location, use pwd for current directory
location="`pwd`"

# Specify playlists that should be downloaded
declare -a playlists=(
	"https://open.spotify.com/PLAYLIST_LINK"  # e.g. Playlist Name
)

# Set client ID and secret
client_id=sampleid123
client_secret=samplesecret123

for playlist in "${playlists[@]}";
do
	echo "Downloading playlist: $playlist"
	docker run --rm \
		   -e SPOTIPY_CLIENT_ID=$client_id \
		   -e SPOTIPY_CLIENT_SECRET=$client_secret \
		   -v "$location":/download \
		   savify \
		   savify "$playlist" -o /download -g "%playlist%" -q best -f mp3 & # Use & for parallel downloading
done
