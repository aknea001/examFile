from signal import signal, SIGTERM
from sys import exit
from time import sleep
import os
from os.path import join, isfile
import json
from apiConnection import APIc

running = True

def shutdown(signum, frame):
    global running
    running = False

def sync(api, syncingFolder: str) -> list:
    import base64

    uploadedDict = api.tableData()
    uploaded = []

    for i in uploadedDict:
        print(i)
        fileName = f"{i['fileName']}.{i['fileExtension']}"
        uploaded.append(fileName)

    downloaded = [f for f in os.listdir() if isfile(join(syncingFolder, f))]

    filesToDownload = []
    filesToUpload = []

    for f in uploaded:
        if f not in downloaded:
            filesToDownload.append(uploaded.index(f))
    
    for f in downloaded:
        if f not in uploaded:
            filesToUpload.append(f)

    for i in filesToDownload:
        result = api.download(i)

        if not result["success"]:
            return
        
        data = result["data"]
        fullname = f"{data['name']}.{data['extension']}"
        with open(join(syncingFolder, fullname), "wb") as f:
            f.write(base64.b64decode(data["data"]))
    
    return uploadedDict

def main():
    signal(SIGTERM, shutdown)

    infoFile = join(os.getcwd(), "info.json")
    if not isfile(infoFile):
        return
    
    with open(infoFile) as f:
        data = json.load(f)
    
    if data["syncing"] == "f":
        return
    
    passwd = data["passwd"]
    token = data["token"]
    syncingFolder = data["syncingFolder"]

    api = APIc("http://100.116.95.27:8000", passwd, token)
    while running:
        for i in range(10):
            if not running:
                break

            sleep(1)
        
        sync(api, syncingFolder)
    
    exit(0)

if __name__ == "__main__":
    main()