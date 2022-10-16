import os
from pathlib import Path
from shutil import move, rmtree
from sys import platform
from uuid import uuid1

FFMPEG_STATIC_LINUX = 'https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz'
FFMPEG_STATIC_WIN = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
FFMPEG_STATIC_MAC = 'https://evermeet.cx/ffmpeg/getrelease/zip'


class FFmpegDL:
    def __init__(self, data: str) -> None:
        self.data_path = Path(data) / 'ffmpeg'

        if platform == 'win32':
            self.temp = self.data_path / str(uuid1())
            self.download_link = FFMPEG_STATIC_WIN
            self.final_location = self.data_path / 'bin' / 'ffmpeg.exe'
            self.platform_task = self._download_win

        elif platform == 'linux':
            self.temp = self.data_path / str(uuid1())
            self.download_link = FFMPEG_STATIC_LINUX
            self.final_location = self.data_path / 'ffmpeg'
            self.platform_task = self._download_linux

        elif platform == 'darwin':
            self.temp = self.data_path / str(uuid1())
            self.download_link = FFMPEG_STATIC_MAC
            self.final_location = self.data_path / 'ffmpeg'
            self.platform_task = self._download_mac

        else:
            raise RuntimeError(f'Platform not supported! [{platform}]')

        self.file = self.temp / self.download_link.split('/')[-1]

    def check_if_file(self) -> bool:
        return self.final_location.is_file()

    def download(self, force=False) -> Path:
        downloaded = self.check_if_file()
        if not downloaded or force:
            rmtree(self.data_path)
            self._download()
            self.platform_task()

        return self.final_location

    def _download(self) -> None:
        from urllib.request import urlretrieve
        self.temp.mkdir(parents=True, exist_ok=True)
        urlretrieve(self.download_link, self.file)

    def _download_win(self) -> None:
        self._unzip()
        bin_path = self.temp / os.listdir(self.temp)[0] / 'bin'
        self._cleanup(bin_path)

    def _download_mac(self) -> None:
        self._unzip()
        bin_file = self.temp / 'ffmpeg'
        self._cleanup(bin_file)

    def _download_linux(self) -> None:
        self._untar()
        bin_file = self.temp / os.listdir(self.temp)[0] / 'ffmpeg'
        self._cleanup(bin_file)

    def _unzip(self) -> None:
        from zipfile import ZipFile
        with ZipFile(self.file, 'r') as zip_ref:
            zip_ref.extractall(self.temp)

    def _untar(self) -> None:
        import tarfile
        with tarfile.open(self.file) as tf:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tf, self.temp)

    def _cleanup(self, ffmpeg_files) -> None:
        move(ffmpeg_files, self.data_path)
        rmtree(self.temp)
