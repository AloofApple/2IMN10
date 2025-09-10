import rpyc
import redis
import os
from rpyc.utils.server import ThreadedServer

PORT = 18861
REDISPORT = 6379

r = redis.Redis(host='redis', port=REDISPORT)

class WordCountService(rpyc.Service):
    def exposed_count_words(self, text: str, keyword: str) -> int:
        key = f"{keyword}-{text}"
        cached = r.get(key)

        if cached:
            print("Cache hit", flush=True)
            count = int(cached)
        else:
            print("Cache miss", flush=True)
            count = text.split().count(keyword) #QUESTION: exact match only?
            r.set(key, count)

        return count

if __name__ == "__main__":
    server = ThreadedServer(WordCountService, port=PORT)
    print(f"WordCount server is running on port {PORT}")
    server.start()