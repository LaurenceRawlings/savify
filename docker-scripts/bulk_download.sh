#!/bin/sh
# This script will download playlist, artists, albums or tracks you specified in parallel. 
# Make sure to customize the variables in the file "config.sh"
# Remove the & at the bottom of the for loop, if you want the script to download them sequentially.
# When starting the script with bash bulk_download.sh, it will create n containers named 
# savify_(last 12 characters of the playlist link) so you can resolve which containers downloads which playlist.

source "config.sh"

for ELEMENT in "${ELEMENTS[@]}";
do
( echo "Downloading element: $ELEMENT"
  ID=${ELEMENT: -8}
  VPN=$(docker ps -a --filter "name=vpn" --filter "health=healthy" --format "table {{.Names}}" | tail -n +2 | xargs shuf -n1 -e)
  if [ -z "$VPN" ]; then
        echo "No VPN found! Running without VPN!"
        docker run --rm -d --name "savify_${ID//[^[:alnum:]]/}" \
                -e SPOTIPY_CLIENT_ID=$CLIENT_ID \
                -e SPOTIPY_CLIENT_SECRET=$CLIENT_SECRET \
                -v "$LOCATION":/download \
                $IMAGE_VERSION \
                "$ELEMENT" -o /download -g "$GROUPING" $OPTIONS
  else
        echo "Using VPN: $VPN"
        docker run --rm -d --name "savify_${ID//[^[:alnum:]]/}_$VPN" \
                --net=container:"$VPN" \
                -e SPOTIPY_CLIENT_ID=$CLIENT_ID \
                -e SPOTIPY_CLIENT_SECRET=$CLIENT_SECRET \
                -v "$LOCATION":/download \
                $IMAGE_VERSION \
                "$ELEMENT" -o /download -g "$GROUPING" $OPTIONS
  fi
) &
done
