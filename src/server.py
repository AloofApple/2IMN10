import rpyc
import os
from rpyc.utils.server import ThreadedServer

PORT = 18861

class WordCountService(rpyc.Service):
    def exposed_count_words(self, text: str) -> int:
        return len(text.split())

if __name__ == "__main__":
    server = ThreadedServer(WordCountService, port=PORT)
    print("WordCount server is running on port PORT...")
    server.start()