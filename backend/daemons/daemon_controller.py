import threading

class DaemonController:

    def __init__(self):
        self.daemons = []

    def register(self, daemon):
        self.daemons.append(daemon)

    def start_all(self):

        for d in self.daemons:
            thread = threading.Thread(target=d.start)
            thread.daemon = True
            thread.start()

    def stop_all(self):

        for d in self.daemons:
            d.stop()
