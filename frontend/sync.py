from signal import signal, SIGTERM
from sys import exit
from time import sleep
import os
from apiConnection import APIc

running = True

def shutdown(signum, frame):
    global running
    running = False

def sync(api) -> list:
    api.testSyncing()

def main():
    signal(SIGTERM, shutdown)

    api = APIc("http://10.0.0.20:8000")
    while running:
        sync(api)

        for i in range(60):
            if not running:
                break

            sleep(1)
    
    exit(0)

if __name__ == "__main__":
    main()