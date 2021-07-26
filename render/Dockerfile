FROM ubuntu:20.04
ARG FUNCTION_DIR="/function"


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

ARG FUNCTION_DIR
RUN mkdir -p ${FUNCTION_DIR}
COPY app/* ${FUNCTION_DIR}
RUN pip3 install \
        --target ${FUNCTION_DIR} \
        awslambdaric

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}

ENV DEBIAN_FRONTEND=noninteractive

COPY ./entry_script.sh /entry_script.sh
ADD aws-lambda-rie /usr/local/bin/aws-lambda-rie
ENTRYPOINT [ "/entry_script.sh" ]

CMD ["app.handler"]