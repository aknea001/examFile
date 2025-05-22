import tkinter as tk
from tkinter import filedialog, messagebox
import base64
from apiConnection import APIc

class Frontend(tk.Tk):
    def __init__(self, apiBaseUrl):
        super().__init__()
        self.title("File Storing")
        self.geometry("640x360")

        self.api = APIc(apiBaseUrl)

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
                errorVar.set(f"{tryRegister['code']: tryRegister['msg']} \nTry again later..")
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

        if not entries:
            tk.Label(self, text="Click Upload to upload a file").pack()
        else:
            count = 0
            for i in entries:
                self.addRow(f"{i['fileName']}.{i['fileExtension']}", count)
                count += 1
        
        self.uploadBtn = tk.Button(self, text="Upload", command=self.upload)
        self.uploadBtn.pack(side="bottom")

    def addRow(self, fileName: str, fileID: int):
        row = tk.Frame(self)

        row.columnconfigure(0, weight=1)

        label = tk.Label(row, text=fileName)
        btn = tk.Button(row, text="Download", width=12, command=lambda: self.download(fileID))
        deleteBtn = tk.Button(row, text="Delete", width=12, command=lambda: self.api.delete(fileID))
        
        label.grid(row=0, column=0, sticky="we")
        btn.grid(row=0, column=1, padx=(0, 2))
        deleteBtn.grid(row=0, column=2)

        row.pack(fill="x", side="top", pady=(3, 0), padx=(0, 2))

        self.latestFileID = fileID

    def getFile(self) -> str | None:
        filePath = filedialog.askopenfilename(title="Select file to upload")
        if not filePath:
            return None
        
        return filePath
    
    def getFoler(self) -> str | None:
        folderPath = filedialog.askdirectory(title="Folder to download file")
        if not folderPath:
            return None
        
        return folderPath

    def upload(self):
        filePath = self.getFile()

        if not filePath:
            return
        
        with open(filePath, "rb") as f:
            text = f.read()

        b64file = base64.b64encode(text).decode()
        
        filename = filePath.split("/")[-1]
        result = self.api.upload(b64file, filename)

        if result["success"]:
            self.addRow(filename, self.latestFileID + 1)
    
    def download(self, fileID: int):
        folderPath = self.getFoler()

        if not folderPath:
            return
        
        result = self.api.download(fileID)

        if not result["success"]:
            return #add error handling later
        
        data = result["data"]
        fullname = f"{data['name']}.{data['extension']}"
        with open(f"{folderPath}/{fullname}", "wb") as f:
            f.write(base64.b64decode(data["data"]))
        
        messagebox.showinfo("Success", f"{fullname} successfully downloaded!")

def main():
    #apiBaseUrl = "chrome-extension://http://https:/api.api/api?api=api"
    apiBaseUrl = "http://100.94.183.127:8000"

    app = Frontend(apiBaseUrl)
    app.mainloop()

if __name__ == "__main__":
    main()