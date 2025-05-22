import requests

class APIc():
    def __init__(self, url: str):
        self.baseUrl = url
        self.passwd = None
        self.token = None
        self.headers = {"Authorization": f"Bearer {self.token}"}

        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def login(self, username: str, passwd: str) -> dict:
        with self.session as s:
            res = s.post(f"{self.baseUrl}/login", json={"username": username, "passwd": passwd})

        if res.status_code != 200:
            return {"success": False, "code": res.status_code, "msg": res.json()["msg"]}
        
        self.token = res.json()["token"]
        self.passwd = passwd
        self.headers["Authorization"] = f"Bearer {self.token}"
        self.session.headers.update(self.headers)
        return {"success": True}

    def register(self, username: str, passwd: str) -> dict:
        with self.session as s:
            res = s.post(f"{self.baseUrl}/register", json={"username": username, "passwd": passwd})
        
        if res.status_code != 201:
            return {"success": False, "code": res.status_code, "msg": res.json()["msg"]}
        
        return {"success": True}

    def upload(self, b64file: str, fileName: str) -> dict:
        with self.session as s:
            res = s.post(f"{self.baseUrl}/upload", json={"fileB64bytes": b64file, "fileName": fileName, "passwd": self.passwd})
        
        if res.status_code != 201:
            print(res.json())
            return {"success": False, "code": res.status_code, "msg": res.json()["msg"]}
        
        return {"success": True}

    def download(self, fileID: int) -> dict:
        # get request, returns b64file
        # idk if ill "download" here or in main frontend
        with self.session as s:
            res = s.post(f"{self.baseUrl}/download", json={"dekDerivation": {"passwd": self.passwd}, "fileID": {"id": fileID}})
        
        if res.status_code != 200:
            return {"success": False, "code": res.status_code, "msg": res.json()["msg"]}
        
        #return {"success": True, "data": res.json()["data"], "name": res.json()["name"], "extension": res.json()["extension"]}
        return {"success": True, "data": res.json()}
    
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