import time
import os

class GitHubIngestionDaemon:

    def __init__(self):
        self.running = False

    def start(self):
        self.running = True
        print("GitHub ingestion daemon started")

        while self.running:
            self.scan()
            time.sleep(300)

    def stop(self):
        self.running = False

    def scan(self):
        print("Scanning GitHub signals...")
