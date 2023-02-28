import sys
import getopt
import os
from os import path

# Define file endings here
DIRETORIES = [
    {"name": '1_Documents', "endings": [
        '.pdf', '.txt', '.doc', '.docx', '.fsxml', '.xml', '.csv', '.xlsx']},
    {"name": '2_Coding', "endings": ['.css', '.js', '.ts', '.json', '.sh', '.bat', '.jar', '.java', '.py', '.yaml', '.yml', '.html' ]},
    {"name": '3_Archives', "endings": ['.rar', '.zip', '.7z', '.tar', '.tar.gz','.bz2','.tgz','.gz']},
    {"name": '4_Images', "endings": ['.jpeg', '.jpg', '.png', '.svg', '.HEIF', '.webp']},
    {"name": '5_Videos', "endings": ['.mkv', '.mpeg', '.avi', '.mp4']},
    {"name": '6_Music', "endings": ['.mp3', '.flak']},
    {"name": '7_Design', "endings": ['.afpub', '.afdesign', '.psd']},
    {"name": '8_Books', "endings": ['.epub', '.mobi']},
    {"name": '9_Other', "endings": ['.nzb', '.log']}
]


ROOTFOLER = ''

def check_directories(folder):
    if not path.exists(folder):
        print('given folder does not exists')
        sys.exit()
    for directory in DIRETORIES:
          for filename in os.listdir(folder):
               file = os.path.join(folder, filename)
               if file.lower().endswith(tuple((directory['endings']))):
                    if not path.exists(f'{folder}/{directory["name"]}'):
                        dir = path.join(folder, directory["name"])
                        os.mkdir(dir)

def sort_files(folder):
    for filename in os.listdir(folder):
         file = os.path.join(folder, filename)
         for directory in DIRETORIES:
             if file.lower().endswith(tuple((directory['endings']))):
                 os.rename(f'{file}',f'{folder}/{directory["name"]}/{filename}')

def main(argv):
    opts, args = getopt.getopt(argv, "hf:", ["folder="])
    for opt, arg in opts:
        if args == None:
            print('test.py -f <folderpath>')
            sys.exit()
        if opt == '-h':
            print('file_structure.py -f <folderpath>')
            sys.exit()
        elif opt in ("-f", "--folder"):
            ROOTFOLER = arg
    print('Structuring folder: ', ROOTFOLER)

    check_directories(ROOTFOLER)
    sort_files(ROOTFOLER)
    
    print("DONE")


if __name__ == "__main__":
    main(sys.argv[1:])
