# Download a playlist

You can use the `savify_playlist.sh` script to download a playlist in the specified folder.

This script reads the client id and the client secret variables for the `.env` file
create a file named `.env` like the provided file `env_example` and put your id and secret in it.

And run this command
```
./savify_playlist.sh <downloads_dir> <playlist_url>
```
For example run :
```
./savify_playlist.sh $HOME/Music/test https://open.spotify.com/playlist/776YUd9aaoOi9h8zWJBrBG
```

> **Note**
> If you can't run the file , do :
> 
> ```
>   chmod +x ./savify_playlist.sh 
> ```
