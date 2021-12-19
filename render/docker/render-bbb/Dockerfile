FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
  apt-get install -y \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev \
  ffmpeg \
  libsm6 \
  libxext6 \
  x264 \
  v4l-utils \
  libv4l-dev \
  libx264-dev \
  python3-pip \
  libopencv-dev \
  python3-opencv -y


RUN mkdir -p /app

COPY app/* /app/
COPY requirements.txt /app/

RUN pip3 install -r /app/requirements.txt
WORKDIR /app

RUN echo 'alias render="python3 /app/overengineered.py"' >> ~/.bashrc

