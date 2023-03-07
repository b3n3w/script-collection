#!/bin/bash

echo "Building image for transcoding pipeline"

FILE_THRESHOLD=2000

docker build  -t transcoding-handler:latest .

docker run --rm \
        --name transcoding-handler \
        -v $(pwd):/app \
        -v :/app/files \
        -v p:/tmp_folder \
        -e FILE_THRESHOLD=$FILE_THRESHOLD \
        -e UPLOAD_DIR=/media/source \
        -e SERVER_URL= \
        -e DOWNLOAD_SOURCE=/media/output \
        -e SSH_USERNAME= \
        -e SSH_PASSWORD= \
        -e DISCORD_TOKEN= \
        transcoding-handler:latest