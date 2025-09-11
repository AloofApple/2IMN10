import rpyc
import redis
import os
from rpyc.utils.server import ThreadedServer

SERVERPORT = 5000
HOSTNAME = "redis"
REDISPORT = 6379
FILES_MAP = {
    0: "textfiles/example.txt",
}
r = redis.Redis(HOSTNAME, REDISPORT)

class WordCountService(rpyc.Service):
    def exposed_count_words(self, file_ref: int, keyword: str) -> int:
        # Open the file based on the reference
        if file_ref not in FILES_MAP:
            raise ValueError(f"Invalid file reference: {file_ref}. Allowed references: {list(FILES_MAP.keys())}")
        
        with open(FILES_MAP[file_ref], "r", encoding="utf-8") as f:
            text = f.read()

        # Check cache for result using a composite key else compute and store
        key = f"{file_ref}-{keyword}"
        cached = r.get(key)

        if cached:
            print("Cache hit")
            count = int(cached)
        else:
            print("Cache miss")
            count = text.split().count(keyword) #QUESTION: exact match only?
            r.set(key, count)

        return count

if __name__ == "__main__":
    server = ThreadedServer(WordCountService, port=SERVERPORT)
    print(f"WordCount server is running on port {SERVERPORT}")
    server.start()