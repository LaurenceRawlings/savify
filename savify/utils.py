from pathlib import Path

__all__ = ['clean', 'create_dir', 'get_download_dir', 'get_temp_dir', 'download_file', 'check_ffmpeg', 'check_env', 'check_file', 'safe_path_string']

def clean(path):
    import os
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                from shutil import rmtree
                rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def create_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def _get_data_dir() -> Path:
    from sys import platform

    home = Path.home()

    if platform == "win32":
        return home / "AppData/Roaming/Savify"
    elif platform == "linux":
        return home / ".local/share/Savify"
    elif platform == "darwin":
        return home / "Library/Application Support/Savify"


def get_download_dir() -> Path:
    download_dir = _get_data_dir() / "downloads"
    create_dir(download_dir)
    return download_dir


def get_temp_dir() -> Path:
    temp_dir = _get_data_dir() / "temp"
    create_dir(temp_dir)
    return temp_dir


def download_file(url: str, extension: str = None) -> Path:
    from uuid import uuid1
    file_path = get_temp_dir() / str(uuid1())

    if extension is not None:
        file_path = file_path.with_suffix(f'.{extension}')

    from urllib.request import urlretrieve
    urlretrieve(url, str(file_path))

    return file_path


def check_ffmpeg() -> bool:
    from shutil import which
    return which('ffmpeg') is not None


def check_env() -> bool:
    from os import environ
    if "SPOTIPY_CLIENT_ID" in environ and "SPOTIPY_CLIENT_SECRET" in environ:
        return True
    else:
        return False


def check_file(path: Path) -> bool:
    if path.is_file():
        return True
    else:
        return False


def safe_path_string(string):
    keepcharacters = " !£$%^&()_-+=,.;'@#~[]{}"
    new_string = ""

    for c in string:
        if c.isalnum() or c in keepcharacters:
            new_string = new_string + c
        else:
            new_string = new_string + "□"
    
    return new_string.rstrip()
