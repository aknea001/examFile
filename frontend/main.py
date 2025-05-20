import tkinter as tk
from apiConnection import APIc

class Frontend(tk.Tk):
    def __init__(self, apiBaseUrl):
        super().__init__()
        self.title("File Storing")
        self.geometry("640x360")

        self.api = APIc(apiBaseUrl)

        self.switchPage("registerPage")
    
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

            if not self.api.login(username, passwd):
                self.loginBtn.grid(row=3)
                errorVar.set("Wrong username or password..")
                return
            
            entries = self.api.tableData()

            self.switchPage("homePage", entries)

        self.usernameLabel = tk.Label(self, text="Username")
        self.usernameEntry = tk.Entry(self, textvariable=usernameVar)

        self.passwdLabel = tk.Label(self, text="Password")
        self.passwdEntry = tk.Entry(self, textvariable=passwdVar, show="*")

        self.errorLabel = tk.Label(self, textvariable=errorVar)
        self.loginBtn = tk.Button(self, text="Login", command=login)

        self.usernameLabel.grid(row=0, column=0)
        self.usernameEntry.grid(row=0, column=1)
        self.passwdLabel.grid(row=1, column=0)
        self.passwdEntry.grid(row=1, column=1)
        self.errorLabel.grid(row=2, column=1)
        self.loginBtn.grid(row=2, column=1)

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

            if not self.api.register(username, passwd):
                self.registerBtn.grid(row=4)
                errorVar.set("Error registering user \nTry again later..")
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

        self.usernameLabel.grid(row=0, column=0)
        self.usernameEntry.grid(row=0, column=1)
        self.passwdLabel.grid(row=1, column=0)
        self.passwdEntry.grid(row=1, column=1)
        self.confirmPasswdLabel.grid(row=2, column=0)
        self.confirmPasswdEntry.grid(row=2, column=1)
        self.errorLabel.grid(row=3, column=1)
        self.registerBtn.grid(row=3, column=1)

    def homePage(self, entries: list):
        pass

def main():
    apiBaseUrl = "chrome-extension://http://https:/api.api/api?api=api"

    app = Frontend(apiBaseUrl)
    app.mainloop()

if __name__ == "__main__":
    main()