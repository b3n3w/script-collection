FROM python:3.10.10-slim-buster

WORKDIR /app

RUN apt-get update && apt-get -y install cron vim jq ffmpeg

COPY src src
COPY requirements.txt requirements.txt
COPY scripts scripts
COPY crontab /etc/cron.d/crontab

RUN pip install -r requirements.txt

RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

ENTRYPOINT [ "scripts/init_files.sh" ]