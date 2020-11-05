import os

DATA_PATH = os.path.join(os.getenv('APPDATA'), 'Savify')
TEMP_PATH = os.path.join(DATA_PATH, 'temp')
SAVE_PATH = os.path.join(DATA_PATH, 'downloads')


def clean(path):
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


def create_dir(path):
    from pathlib import Path
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)


def download_file(url, extension=None):
    from uuid import uuid1
    file_path = f'{TEMP_PATH}/{str(uuid1())}'

    if extension != None:
        file_path += f'.{extension}'

    create_dir(file_path)

    from urllib.request import urlretrieve
    urlretrieve(url, file_path)

    return file_path


def check_ffmpeg():
    from shutil import which
    return which('ffmpeg') is not None


def check_file(path):
    from pathlib import Path
    if Path(path).is_file():
        return True
    else:
        return False
