import tkinter as tk

class Frontend(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Storing")
        self.geometry("640x360")
    
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
    app = Frontend()
    app.mainloop()

if __name__ == "__main__":
    main()