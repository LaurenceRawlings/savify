#!/bin/sh

# This script will download playlist, artists, albums or tracks you specified in parallel. 
# Remove the & at the bottom of the for loop, if you want the script to download them sequentially.
# When starting the script with bash download_playlists.sh, it will create n containers named 
# savify_(last 12 characters of the playlist link) so you can resolve which containers downloads which playlist.

# Information: The docker image has to be previously built and tagged with savify[:dev]
# Use 'docker build -t savify:dev .' inside the project directory to build the Docker container
# Or use the Docker image provided in Docker Hub: laurencerawlings/savify:latest (recommended!)

# Specify download location, use pwd for current directory
location="`pwd`"
# Specify grouping schema
grouping="%artist%/%album%"

# Declare list with elements to download, use comment to stay organized!
declare -a elements=(
          "https://open.spotify.com/playlist"  # Element name
          "https://open.spotify.com/album"     # Element name
)

# Set client ID and secret
client_id=sampleid123
client_secret=samplesecret123

# Specify the image you want Savify to run with
image_version=laurencerawlings/savify:latest

for element in "${elements[@]}";
do
( echo "Downloading element: $element"
  id=${element: -8}
  vpn=$(docker ps -a --filter "name=vpn" --filter "health=healthy" --format "table {{.Names}}" | tail -n +2 | xargs shuf -n1 -e)
  if [ -z "$vpn" ]; then
        echo "No VPN found! Running without VPN!"
        docker run --rm -d --name "savify_${id//[^[:alnum:]]/}" \
                -e SPOTIPY_CLIENT_ID=$client_id \
                -e SPOTIPY_CLIENT_SECRET=$client_secret \
                -v "$location":/download \
                $image_version \
                "$element" -o /download -g "$grouping" -m
  else
        echo "Using VPN: $vpn"
        docker run --rm -d --name "savify_${id//[^[:alnum:]]/}_$vpn" \
                --net=container:"$vpn" \
                -e SPOTIPY_CLIENT_ID=$client_id \
                -e SPOTIPY_CLIENT_SECRET=$client_secret \
                -v "$location":/download \
                $image_version \
                "$element" -o /download -g "$grouping" -m
  fi
) &
done
