import os, logging, utils as utils
import shutil

from scp import SCPClient

ssh = utils._setup_sshClient()
utils._setup_logger()

source_dir = os.getenv("DOWNLOAD_SOURCE")


def download_file(source_file):
    logging.info(f"Trying to download {source_file}")
    try:
        with SCPClient(ssh.get_transport()) as scp:
            scp.get(f"{source_dir}/{source_file}", f"/tmp_folder/{source_file}")

        file = utils.find_file_from_json(source_file)
        newFileName = f'{utils.extract_name_without_ext(file["path"])}.mkv'
        logging.info(f'Moving {file["fileName"]} to {newFileName}')
        try:
            shutil.move(f"/tmp_folder/{source_file}", f"{newFileName}")
            logging.info(f'Sucessfully moved {file["fileName"]}.')
            _cleanup(source_file, file)

        except Exception as e:
            logging.error(f"Could not move file: {e}")
        utils.send_success_notification(file, newSize=os.path.getsize(newFileName))

    except Exception as e:
        logging.error(f"Download failed: {e}")


def initiate_download():
    fileCount = utils.check_if_files_to_download(ssh, source_dir)
    if fileCount > 0:
        stdin, stdout, stderr = ssh.exec_command(f"ls -t {source_dir}")
        newest_file = stdout.readline().strip()
        download_file(newest_file)
    else:
        logging.info("No files to download at the moment")
        return


def _cleanup(newFileName, file):
    logging.info("Removing artifacts and old files")
    try:
        utils.remove_file_from_remote(ssh, newFileName)
    except Exception as e:
        logging.error(f"Could not remove file from remote folder: {e}")
    try:
        hashName = utils.extract_name_without_ext(file["hashName"])
        utils.remove_entry_from_json("hashName", hashName, "uploaded.json")
        utils.remove_entry_from_json("path", file["path"], "files_big.json")
    except:
        logging.error("Could not remove entry from json.")


initiate_download()
