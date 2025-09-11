import rpyc
import redis
import os
from rpyc.utils.server import ThreadedServer

SERVERPORT = 5000
HOSTNAME = "redis"
REDISPORT = 6379

r = redis.Redis(HOSTNAME, REDISPORT)

class WordCountService(rpyc.Service):
    def exposed_count_words(self, text: str, keyword: str) -> int:
        key = f"{keyword}-{text}"
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