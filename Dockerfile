FROM python:3.9.2-slim-buster

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ="Asia/Kolkata"

RUN apt-get update && \
    apt-get install -y aria2 tzdata git wget ffmpeg build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN python3 -m pip install --upgrade pip && \
    pip3 install -r requirements.txt

CMD ["python3", "-m", "bot"]