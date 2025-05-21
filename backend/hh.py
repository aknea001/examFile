class HardwareHash():
    def __init__(self):
        import hashlib

        self.getHHdata()

        self.hhData = self.serial + self.revision
        hashObject = hashlib.sha256(self.hhData.encode())
        self.hhHashed = hashObject.digest()

    def getHHdata(self):
        with open("/proc/cpuinfo", "r") as f:
            for line in f.readlines():
                if line.startswith("Serial"):
                    self.serial = str(line.strip().split(": ")[1])
                    continue

                if line.startswith("Revision"):
                    self.revision = str(line.strip().split(": ")[1])
                    continue
                    
    def getKEK(self, passwd: bytes, salt: bytes) -> bytes:
        from argon2.low_level import hash_secret_raw, Type
        from Crypto.Random import get_random_bytes

        secret = passwd + self.hhHashed
        
        self.key = hash_secret_raw(
            secret=secret,
            salt=salt,
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            type=Type.ID
        )

        return self.key