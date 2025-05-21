import requests

class APIc():
    def __init__(self, url: str):
        self.baseUrl = url
        self.token = None
        self.headers = {"Authorization": self.token}

        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def login(self, username: str, passwd: str) -> dict:
        with self.session as s:
            res = s.post(f"{self.baseUrl}/login", json={"username": username, "passwd": passwd})

        if res.status_code != 200:
            return {"status": False, "code": res.status_code, "msg": res.json()["msg"]}
        
        self.token = res.json()["token"]
        return {"status": True}

    def register(self, username: str, passwd: str) -> dict:
        # post request, doesnt necessarily return anything
        # 201 = success
        with self.session as s:
            res = s.post(f"{self.baseUrl}/register", json={"username": username, "passwd": passwd})
        
        if res.status_code != 201:
            return {"status": False, "code": res.status_code, "msg": res.json()["msg"]}
        
        return {"status": True}

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
    
    def delete(self, fileID: int):
        # delete request, doesnt necessarily return anything
        # 204 = success
        pass

    def tableData(self) -> list:
        # get request, returns list of files user has uploaded
        # f eks: [{"fileName": "contract", "fileExtension": "mp3"}, {"fileName": "essay", "fileExtension": "jpeg"}, {"fileName": "ytVid", "fileExtension": "pdf"}]
        return [{"fileName": "contract", "fileExtension": "mp3"}, {"fileName": "essay", "fileExtension": "jpeg"}, {"fileName": "ytVid", "fileExtension": "pdf"}]
    
if __name__ == "__main__":
    api = APIc("http://localhost:8000")
    api.test()