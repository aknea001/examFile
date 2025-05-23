import tkinter as tk
from tkinter import filedialog, messagebox
import base64
from os import getcwd, remove, listdir, kill
from os.path import isfile, join
from signal import SIGTERM
import subprocess
import json
from apiConnection import APIc
from sync import sync
import psutil

class Frontend(tk.Tk):
    def __init__(self, apiBaseUrl):
        super().__init__()
        self.title("File Storing")
        self.geometry("640x360")

        self.api = APIc(apiBaseUrl)

        self.infoFile = join(getcwd(), "info.json")
        if isfile(self.infoFile):
            with open(self.infoFile, "r") as f:
                data = json.load(f)

            username = data["username"]
            passwd = data["passwd"]
            self.syncing = data["syncing"]
            self.syncingFolder = data["syncingFolder"]
            checkCreds = self.api.login(username, passwd)

            if not checkCreds["success"]:
                remove(self.infoFile)
                self.switchPage("loginPage")
                return
            
            if self.syncing == "t":
                try:
                    process = psutil.Process(int(data["syncingpid"]))

                    if process.name() == "python":
                        running = True
                    else:
                        running = False
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    running = False
                
                if not running:
                    pid = self.startSyncing()

                    data["syncingpid"] = pid

                    with open(self.infoFile, "w") as f:
                        newData = json.dumps(data, indent=4)
                        f.write(newData)

            entries = self.api.tableData()
            self.switchPage("homePage", entries)
            return

        self.switchPage("loginPage")
    
    def switchPage(self, pageName: str, *args):
        for widget in self.winfo_children():
            widget.destroy()
        
        newPage = getattr(self, pageName)
        newPage(*args)
    
    def loginPage(self):
        usernameVar = tk.StringVar()
        passwdVar = tk.StringVar()
        errorVar = tk.StringVar()

        def login():
            username = usernameVar.get()
            passwd = passwdVar.get()

            checkCreds = self.api.login(username, passwd)

            if not checkCreds["success"]:
                self.loginBtn.grid(row=3)
                errorVar.set(f"{checkCreds['code']}: {checkCreds['msg']}")
                return
            
            with open(self.infoFile, "w") as f:
                data = json.dumps({
                                    "username": username, 
                                    "passwd": passwd,
                                    "token": self.api.token,
                                    "syncing": "f",
                                    "syncingFolder": ""
                                    }, indent=4)
                self.syncing = "f"
                self.syncingFolder = ""
                f.write(data)
            
            entries = self.api.tableData()

            self.switchPage("homePage", entries)

        self.usernameLabel = tk.Label(self, text="Username")
        self.usernameEntry = tk.Entry(self, textvariable=usernameVar)

        self.passwdLabel = tk.Label(self, text="Password")
        self.passwdEntry = tk.Entry(self, textvariable=passwdVar, show="*")

        self.errorLabel = tk.Label(self, textvariable=errorVar)
        self.loginBtn = tk.Button(self, text="Login", command=login)

        self.registerBtn = tk.Button(self, text="Create account", command=lambda: self.switchPage("registerPage"))

        self.usernameLabel.grid(row=0, column=0)
        self.usernameEntry.grid(row=0, column=1)
        self.passwdLabel.grid(row=1, column=0)
        self.passwdEntry.grid(row=1, column=1)
        self.errorLabel.grid(row=2, column=1)
        self.loginBtn.grid(row=2, column=1)
        self.registerBtn.grid(row=4, column=1, pady=20)

    def logout(self):
        self.api.token = None
        self.api.passwd = None

        if self.syncing == "t":
            self.stopSyncing([])

        if isfile(self.infoFile):
            remove(self.infoFile)

        self.switchPage("loginPage")

    def registerPage(self):
        usernameVar = tk.StringVar()
        passwdVar = tk.StringVar()
        confirmPasswdVar = tk.StringVar()
        errorVar = tk.StringVar()

        def register():
            username = usernameVar.get()
            passwd = passwdVar.get()
            confirmPasswd = confirmPasswdVar.get()

            if passwd != confirmPasswd:
                self.registerBtn.grid(row=4)
                errorVar.set("Passwords not matching..")
                return

            tryRegister = self.api.register(username, passwd)
            if not tryRegister["success"]:
                self.registerBtn.grid(row=4)
                errorVar.set(f"{tryRegister['code']}: {tryRegister['msg']} \nTry again later..")
                return

            self.switchPage("loginPage")

        self.usernameLabel = tk.Label(self, text="Username")
        self.usernameEntry = tk.Entry(self, textvariable=usernameVar)

        self.passwdLabel = tk.Label(self, text="Password")
        self.passwdEntry = tk.Entry(self, textvariable=passwdVar, show="*")

        self.confirmPasswdLabel = tk.Label(self, text="Confirm Password")
        self.confirmPasswdEntry = tk.Entry(self, textvariable=confirmPasswdVar, show="*")

        self.errorLabel = tk.Label(self, textvariable=errorVar)
        self.registerBtn = tk.Button(self, text="Register", command=register)

        self.loginBtn = tk.Button(self, text="Already have an account", command=lambda: self.switchPage("loginPage"))

        self.usernameLabel.grid(row=0, column=0)
        self.usernameEntry.grid(row=0, column=1)
        self.passwdLabel.grid(row=1, column=0)
        self.passwdEntry.grid(row=1, column=1)
        self.confirmPasswdLabel.grid(row=2, column=0)
        self.confirmPasswdEntry.grid(row=2, column=1)
        self.errorLabel.grid(row=3, column=1)
        self.registerBtn.grid(row=3, column=1)
        self.loginBtn.grid(row=5, column=1, pady=20)

    def homePage(self, entries: list):
        self.menuBar = tk.Menu(self)
        self.config(menu=self.menuBar)

        self.menuBar.add_command(label="Logout", command=self.logout)

        if self.syncing == "f":
            self.menuBar.add_command(label="Enable syncing", command=lambda: self.enableSync(entries))
        else:
            self.syncingMenu = tk.Menu(self.menuBar, tearoff=0)
            self.menuBar.add_cascade(label="Syncing", menu=self.syncingMenu)

            self.syncingMenu.add_command(label="Stop syncing", command=lambda: self.stopSyncing(entries))
            self.syncingMenu.add_command(label="Manual sync", command=self.manualSync)
            self.syncingMenu.add_command(label="Test3")

        if not entries:
            self.uploadLabel = tk.Label(self, text="Click Upload to upload a file")
            self.uploadLabel.pack()
            self.latestFileID = -1
        else:
            count = 0
            for i in entries:
                fullName = f"{i['fileName']}.{i['fileExtension']}"
                self.addRow(fullName, count)
                count += 1
        
        self.uploadBtn = tk.Button(self, text="Upload", command=self.upload)
        self.uploadBtn.pack(side="bottom")

    def addRow(self, fileName: str, fileID: int):
        row = tk.Frame(self)

        row.columnconfigure(0, weight=1)

        label = tk.Label(row, text=fileName)
        btn = tk.Button(row, text="Download", width=12, command=lambda: self.download(fileID))
        deleteBtn = tk.Button(row, text="Delete", width=12, command=lambda: self.delete(fileID, fileName, row))
        
        label.grid(row=0, column=0, sticky="we")
        btn.grid(row=0, column=1, padx=(0, 2))
        deleteBtn.grid(row=0, column=2)

        row.pack(fill="x", side="top", pady=(3, 0), padx=(0, 2))

        self.latestFileID = fileID

    def getFile(self, title: str) -> str | None:
        filePath = filedialog.askopenfilename(title=title)
        if not filePath:
            return None
        
        return filePath
    
    def getFolder(self, title: str) -> str | None:
        folderPath = filedialog.askdirectory(title=title)
        if not folderPath:
            return None
        
        return folderPath

    def upload(self):
        filePath = self.getFile("Select file to upload")

        if not filePath:
            return
        
        with open(filePath, "rb") as f:
            text = f.read()

        b64file = base64.b64encode(text).decode()
        
        filename = filePath.split("/")[-1]
        result = self.api.upload(b64file, filename)

        if result["success"]:
            self.addRow(filename, self.latestFileID + 1)
            if self.latestFileID == 0:
                self.uploadLabel.destroy()
    
    def download(self, fileID: int):
        folderPath = self.getFolder("Select folder to download file in")

        if not folderPath:
            return
        
        result = self.api.download(fileID)

        if not result["success"]:
            return # add error handling later
        
        data = result["data"]
        fullname = f"{data['name']}.{data['extension']}"
        with open(f"{folderPath}/{fullname}", "wb") as f:
            f.write(base64.b64decode(data["data"]))
        
        messagebox.showinfo("Success", f"{fullname} successfully downloaded!")
    
    def delete(self, fileID: int, fileName: str, row):
        confirm = messagebox.askokcancel("Are you sure?", f"Are you sure you want to delete {fileName} \nThis action is permanent")
        if not confirm:
            return
        
        result = self.api.delete(fileID)

        if not result["success"]:
            return # add error handling later
        
        row.destroy()

    def enableSync(self, entries: list):
        folder = self.getFolder("Select folder to sync against")
        
        if not folder:
            return
        
        self.syncing = "t"
        self.syncingFolder = folder

        currentFiles = []

        for f in listdir(folder):
            if isfile(join(folder, f)):
                currentFiles.append(f)

        filesToUpload = []
        filesToDownload = []

        for f in currentFiles:
            if f not in entries:
                filesToUpload.append(f)

        for f in entries:
            if f not in currentFiles:
                filesToDownload.append(f)

        print(filesToUpload)
        print(filesToDownload)

        pid = self.startSyncing()

        with open(self.infoFile, "r") as f:
            data = json.load(f)
        
        data["syncing"] = self.syncing
        data["syncingFolder"] = self.syncingFolder
        data["syncingpid"] = pid

        with open(self.infoFile, "w") as f:
            newData = json.dumps(data, indent=4)
            f.write(newData)

        self.syncing = "t"

        self.switchPage("homePage", entries)

    def startSyncing(self) -> str:
        process = subprocess.Popen(["python", join(getcwd(), "sync.py")])
        pid = str(process.pid)

        return pid

    def stopSyncing(self, entries: list):
        with open(self.infoFile, "r") as f:
            data = json.load(f)
        
        pid = data["syncingpid"]
        kill(int(pid), SIGTERM)

        data["syncing"] = "f"
        data["syncingFolder"] = ""
        data["syncingpid"] = ""

        with open(self.infoFile, "w") as f:
            newData = json.dumps(data, indent=4)
            f.write(newData)
        
        self.syncing = "f"
        
        self.switchPage("homePage", entries)
    
    def manualSync(self):
        newEntries = sync(self.api)

        self.switchPage("homePage", newEntries)

def main():
    #apiBaseUrl = "chrome-extension://http://https:/api.api/api?api=api"
    apiBaseUrl = "http://100.116.95.27:8000"

    app = Frontend(apiBaseUrl)
    app.mainloop()

if __name__ == "__main__":
    main()