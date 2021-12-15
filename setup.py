#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages, Extension

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = ['ffmpy>=0.3.0', 'spotipy>=2.16.1', 'tldextract>=3.1.0', 'validators>=0.18.2', 'yt-dlp>=2021.12.1',
                'requests>=2.25.1', 'click>=7.1.2']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Laurence Rawlings",
    author_email='contact@laurencerawlings.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Download Spotify songs to mp3 with full metadata and cover art!",
    entry_points={
        'console_scripts': [
            'savify=savify.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='savify, spotify, downloader, mp3, save, playlist',
    name='savify',
    packages=find_packages(include=['savify', 'savify.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/LaurenceRawlings/savify',
    version='2.4.0',
    zip_safe=False,
)
