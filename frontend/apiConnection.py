import requests

class APIc():
    def __init__(self, url: str):
        self.baseUrl = url
        self.token = None
        self.headers = {"Authorization": self.token}

        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def login(self, username: str, passwd: str):
        # post request, returns jwt token
        # self.token = res.json()["token"]
        pass

    def register(self, username: str, passwd: str):
        # post request, doesnt necessarily return anything
        # 201 = success
        pass

    def upload(self, b64file: str, fileName: str):
        # post request, doesnt necessarily return anything
        # 201 = success
        pass

    def download(self, fileID: int):
        # get request, returns b64file
        # idk if ill "download" here or in main frontend

        # if download == here:
        #       func.parameter.append(newLocation: str)
        pass

    def tableData(self):
        # get request, returns list of files user has uploaded
        # f eks: [{"fileName": "contract", "fileExtension": "mp3"}, {"fileName": "essay", "fileExtension": "jpeg"}, {"fileName": "ytVid", "fileExtension": "pdf"}]
        pass
    
if __name__ == "__main__":
    api = APIc("http://localhost:8000")
    api.test()