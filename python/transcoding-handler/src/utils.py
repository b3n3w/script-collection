import logging, os, json, sys, paramiko, math, time
from discord_webhook import DiscordWebhook, DiscordEmbed

def extract_basename(path):
    return os.path.basename(path)


def extract_name_without_ext(filename):
    return os.path.splitext(filename)[0]


def check_if_file_is_video(path):
    return os.path.isfile(path) and path.endswith(".mp4") or path.endswith(".mkv")


def find_file_from_json(fullName):
    try:
        filename = extract_name_without_ext(fullName)
        with open("/app/uploaded.json") as fp:
            json_o = json.load(fp)
            for file in json_o:
                if extract_name_without_ext(file["hashName"]) == filename:
                    return file
            logging.error("File in uploaded.json not found.")
    except:
        logging.error("Could not find uploaded.json")
        return


def store_video_information_to_json(videoInformation):
    listObj = []
    filename = "/app/uploaded.json"
    # Check if file exists
    if os.path.exists(filename):
        # Read JSON file
        with open(filename) as fp:
            listObj = json.load(fp)

        listObj.append(videoInformation)

        with open(filename, "w") as json_file:
            json.dump(listObj, json_file, indent=4, separators=(",", ": "))
    else:
        arr = [videoInformation]
        json_o = json.dumps(arr, indent=2)

        with open("uploaded.json", "w") as outfile:
            outfile.write(json_o)
        return


def remove_file_from_remote(ssh, filename):
    source_dir = os.getenv("DOWNLOAD_SOURCE")
    sftp = ssh.open_sftp()
    sftp.remove(f"{source_dir}/{filename}")
    sftp.close()
    ssh.close()
    logging.info(f"Removed {source_dir}/{filename}")


def remove_entry_from_json(key, value, jsonfile):
    try:
        with open(jsonfile, "r") as f:
            data = json.load(f)
            data = [obj for obj in data if obj[key] != value]
            with open(jsonfile, "w") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        logging.error(f"Could not remove entry from {jsonfile}: {e}")


def check_if_files_to_download(ssh, remote_path):
    # execute command to list all files in the directory
    stdin, stdout, stderr = ssh.exec_command(f"ls {remote_path}")

    # read the output and split it into a list of filenames
    filenames = stdout.read().decode().strip().split()

    # check if any filename has a .mkv extension
    if any(filename.endswith(".mkv") for filename in filenames):
        return True
    else:
        return False


def find_file_on_remote(ssh, filename):
    sftp = ssh.open_sftp()
    try:
        sftp.stat(filename)
        return True
    except FileNotFoundError:
        sftp.close()
        return False


def _convert_size(size_bytes):
    size_bytes = int(size_bytes)
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def _setup_logger():
    root = logging.getLogger()
    if root.hasHandlers():
        root.handlers.clear()

    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root.addHandler(handler)


def _setup_sshClient() -> paramiko.SSHClient:
    ssh = paramiko.SSHClient()
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        os.getenv("SERVER_URL"),
        22,
        os.getenv("SSH_USERNAME"),
        os.getenv("SSH_PASSWORD"),
    )

    return ssh


def send_basic_notification(title, message, color):
    try:
        embed = DiscordEmbed(title=title, description=message, color=color)
        webhook = DiscordWebhook(url=os.getenv("DISCORD_TOKEN"), rate_limit_retry=True)

        webhook.add_embed(embed)
        response = webhook.execute()
    except Exception as e:
        logging.error(f"Could not send discord notification: {e}")



def send_success_notification(file, newSize):
    oldSize = file["size"]
    fileName = extract_basename(file["path"])

    webhook = DiscordWebhook(url=os.getenv("DISCORD_TOKEN"), username="Transcodi")

    embed = DiscordEmbed(
        title="Succesfully transcoded file:",
        description=f"{fileName} has been transcoded.",
        color="03f834",
    )
    embed.set_author(name="Transcodii")

    embed.set_footer(
        text=f'Started: {file["time_hashed"]}, Ended: {time.ctime(time.time())}'
    )
    embed.set_timestamp()
    embed.add_embed_field(name="Old size", value=_convert_size(oldSize))
    embed.add_embed_field(name="New Size", value=_convert_size(newSize))

    webhook.add_embed(embed)
    response = webhook.execute()


_setup_logger()
