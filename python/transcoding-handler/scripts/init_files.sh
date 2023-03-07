#!/bin/bash

DIR=/app/files

if [ ! "$(ls -A $DIR)" ]; then
    echo "No files to scan. Please use correct folder"
    exit 1
fi;

if [[ -z $FILE_THRESHOLD ]];then
    echo "File threshold for big files not set. Exit"
    exit 1
fi

function _extracting_h264_files(){

_formatted_size="$(( ${FILE_THRESHOLD%% *} / 1024)) MB"
echo "Checking for h264 codec files bigger than $_formatted_size"

#
# Find all .mkv and .mp4 files, which have the codec h264 and put them as object into /app/tmp.json
# Object keys: 
#   - path
#   - size
#   - codec
#
echo $(find $DIR -type f -regextype posix-extended -regex '.*.(mkv|mp4)' -exec \
    ffprobe -v quiet -show_streams -show_format -of json {} \; | \
    jq -c '.format.filename as $path | .format.size as $size | .streams[]? | select(.codec_type=="video" and .codec_name=="h264") | {codec: .codec_name, path: $path, size: $size}') > /app/tmp.json
    
# REformat tmp.json into object array
sed 's/,$//' /app/tmp.json | jq -s . > /app/files.json

# Extracting biggest files by threshold
jq '.[] | select((.size|tonumber) >= '"$FILE_THRESHOLD"')' files.json | jq -s . > /app/files_big.json
FILE_COUNT=$(grep -ic '"codec": "h264"' /app/files_big.json || true)

if [[ $FILE_COUNT == "0" ]];then
    echo "No files to transcode. Exit now."
    exit 1
fi;

echo "$FILE_COUNT files are bigger than filesize threshold."
rm /app/tmp.json /app/files.json

}

_extracting_h264_files

# Make environment variables accessible from cronjob
env >> /etc/environment

## Setup logs

# Create custom stdout and stderr named pipes
mkfifo /tmp/stdout /tmp/stderr
chmod 0666 /tmp/stdout /tmp/stderr

# Have the main Docker process tail the files to produce stdout and stderr 
# for the main process that Docker will actually show in docker logs.
tail -f /tmp/stdout &
tail -f /tmp/stderr >&2 &

# Start upload when starting container
/usr/local/bin/python3.10 /app/src/upload.py > /tmp/stdout 2> /tmp/stderr

echo "Starting cronjobs now.."
cron -f