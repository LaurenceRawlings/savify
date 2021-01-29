# Use an official Python runtime as a base image
FROM python:3.8-slim

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y git ffmpeg

# Clone git repo
RUN git clone https://github.com/LaurenceRawlings/savify
WORKDIR /savify

# Install dependencies and setup savify from source
RUN pip3 install requests --upgrade
RUN python3 setup.py install

# Define environment variable as placeholder variables
ENV SPOTIPY_CLIENT_ID=
ENV SPOTIPY_CLIENT_SECRET=

# Execute savify when container is started
ENTRYPOINT ["/usr/local/bin/savify"]
# Automatically print help if container is started without arguments
CMD ["--help"]
