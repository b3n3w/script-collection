# File-Structurer
   
Tool to sort files in a directory into categories. Can be useful when downloading different files into one directory.

If you want to sort your downloaded files once every hour, put this into your cronjobs.

```bash
crontab -e
```

```bash
1 * * * * python3 ~/file_structur.py -f ~/Downloads > /tmp/listener.log 2>&1
```
