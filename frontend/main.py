import tkinter as tk
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
        pass

    def registerPage(self):
        pass

    def homePage(self):
        pass

def main():
    apiBaseUrl = "chrome-extension://http://https:/api.api/api?api=api"

    app = Frontend(apiBaseUrl)
    app.mainloop()

if __name__ == "__main__":
    main()