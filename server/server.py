import rpyc
import redis
import logging 
from rpyc.utils.server import ThreadedServer
import threading

############################################################################################################
# Setup
#

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S"
)

SERVERPORT = 5000
HOSTNAME = "redis"
REDISPORT = 6379
FILES_MAP = {
    0: "textfiles/example.txt",
}
r = redis.Redis(HOSTNAME, REDISPORT)

############################################################################################################
# Service
#

class WordCountService(rpyc.Service):
    active_clients = 0
    lock = threading.Lock()

    def on_connect(self, conn):
        with self.lock:
            WordCountService.active_clients += 1

    def on_disconnect(self, conn):
        with self.lock:
            WordCountService.active_clients -= 1

    def exposed_count_words(self, file_ref: int, keyword: str) -> int:
        # Open the file based on the reference
        if file_ref not in FILES_MAP:
            logging.error(f"invalid file reference: {file_ref}. Allowed references: {list(FILES_MAP.keys())}")
            raise ValueError(f"invalid file reference: {file_ref}. Allowed references: {list(FILES_MAP.keys())}")
        
        with open(FILES_MAP[file_ref], "r", encoding="utf-8") as f:
            text = f.read()

        # Check cache for result using a composite key else compute and store
        key = f"{file_ref}-{keyword}"
        cached = r.get(key)

        if cached:
            count = int(cached)
            logging.info(f"response keyword='{keyword}' in file_ref={file_ref} has count={count} (😀 cache HIT)")
        else:
            count = text.split().count(keyword)  # exact match only???
            r.set(key, count)
            logging.info(f"response keyword='{keyword}' in file_ref={file_ref} has count={count} (😔 cache MISS)")

        return count
    
    def exposed_get_active_clients(self) -> int:
        with self.lock:
            return WordCountService.active_clients

if __name__ == "__main__":
    server = ThreadedServer(WordCountService, port=SERVERPORT)
    print(f"server is running on port {SERVERPORT}")
    server.start()