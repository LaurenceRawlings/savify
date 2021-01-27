# Use an official Python runtime as a base image
FROM python:3.8-slim

# Install software
RUN apt-get update
RUN apt-get install -y ffmpeg
RUN pip3 install savify --upgrade

# Define environment variable
ENV SPOTIPY_CLIENT_ID=
ENV SPOTIPY_CLIENT_SECRET=
