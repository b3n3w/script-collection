import os, logging, utils as utils, time
import hashlib, json

from scp import SCPClient

utils._setup_logger()
ssh = utils._setup_sshClient()


def upload_file(file):
    if utils.find_file_on_remote(ssh, file["hashName"]):
        logging.info(
            f'{file["fileName"]} already exists on the remote folder. Skip upload'
        )
        return
    try:
        logging.info("Trying to upload file: {fileName} as {hashName}.".format(**file))

        start = time.process_time()
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(file["path"], f'{os.getenv("UPLOAD_DIR")}/{file["hashName"]}')
        spent = time.process_time() - start

        # Store to uploaded.json
        utils.store_video_information_to_json(file)

        logging.info(f'Sucessfully uploaded: {file["fileName"]} in {spent}s \n')

        utils.send_basic_notification(
            title="Added new file to queue",
            message=f" File: {file['fileName']} Size: {utils._convert_size(file['size'])}",
            color="00B9DE",
        )

    except Exception as e:
        logging.error("Upload failed: {}".format(file))


def extract_file(index):
    try:
        with open("/app/files_big.json") as big_json:
            data = json.load(big_json)

            if len(data) == 0:
                logging.info("No more files to transcode")
                utils.send_basic_notification(
                    title="Info",
                    message=f"No more files to transcode. Please change sourcefolder",
                    color="DE9800",
                )
                return

            file = data[index]
            if utils.check_if_file_is_video(file["path"]):
                videoName = utils.extract_basename(file["path"])
                extension = os.path.splitext(videoName)[1][1:].strip()

                str = hashlib.sha256(file["path"].encode("utf-8"))
                hash_name = str.hexdigest() + f".{extension}"
                extracted_file = {
                    "fileName": videoName,
                    "hashName": hash_name,
                    "path": file["path"],
                    "size": file["size"],
                    "time_hashed": time.ctime(time.time()),
                }
                return extracted_file
            else:
                logging.info("File is no video file.")

    except Exception as Argument:
        logging.error(f"Error while loading files_big.json: {Argument}")


def main():
    try:
        if os.getenv("UPLOAD_COUNT") is None:
            file = extract_file(index=0)
            upload_file(file)
        else:
            for i in range(int(os.getenv("UPLOAD_COUNT"))):
                file = extract_file(index=i)
                upload_file(file)
    except Exception as e:
        return


main()
