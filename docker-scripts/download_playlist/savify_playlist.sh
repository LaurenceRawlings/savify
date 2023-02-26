#!/bin/bash
# This script will download all the songs in a playlist
# Usage: ./savify_playlist.sh <downloads_dir> <playlist_url>
# Example: ./savify_playlist.sh $HOME/Music/test https://open.spotify.com/playlist/776YUd9aaoOi9h8zWJBrBG
DOWNLOADS_DIR=$1
export $(grep -v '^#' .env | xargs) # This will export all the environment variables from .env file
docker run --rm -v $DOWNLOADS_DIR:/root/.local/share/Savify/downloads -e SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID -e SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET laurencerawlings/savify:latest "$2"

