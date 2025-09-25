import rpyc
import redis
import logging 
import re
import argparse
from typing import Tuple
from rpyc.utils.server import ThreadedServer

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
    "bee_movie": "textfiles/bee_movie_script.txt",
    "shakespeare": "textfiles/shakespeare.txt"
}
r = redis.Redis(host=HOSTNAME, port=REDISPORT, db=0)

############################################################################################################
# Service
#

class WordCountService(rpyc.Service):
    def exposed_count_words(self, file_ref: str, keyword: str) -> Tuple[int, bool]:
        cache_miss = False

        # Open the file based on the reference
        if file_ref not in FILES_MAP:
            logging.error(f"invalid file reference: {file_ref}. Allowed references: {list(FILES_MAP.keys())}")
            raise ValueError(f"invalid file reference: {file_ref}. Allowed references: {list(FILES_MAP.keys())}")

        # Check cache for result using a composite key else compute and store
        key = f"{file_ref}-{keyword}"
        cached = r.get(key)

        # Use regex to count whole word matches only so it ignores punctuation
        if cached:
            count = int(cached)
            logging.info(f"response keyword='{keyword}' in file_ref={file_ref} has count={count} (cache HIT) 😀")
        else:

            # The double cache check cause in most cases the cache shouldn't be locked but when it is missed only one should be 
            # doing the calculation.
            lock = r.lock(f"lock:{key}", timeout=10)

            with lock:
                cached = r.get(key)
                
                if cached:
                    count = int(cached)
                    logging.info(f"response keyword='{keyword}' in file_ref={file_ref} has count={count} (cache HIT) 😀")
                else:
                    with open(FILES_MAP[file_ref], "r", encoding="utf-8") as f:
                        text = f.read()

                    cache_miss = True
                    words = re.findall(r'\b\w+\b', text.lower())
                    count = words.count(keyword.lower())
                    r.set(key, count)
                    logging.info(f"response keyword='{keyword}' in file_ref={file_ref} has count={count} (cache MISS) 😔")

        return count, cache_miss

if __name__ == "__main__":
    server = ThreadedServer(WordCountService, port=SERVERPORT, logger=None)

    logging.info(f"Connected to Redis at {HOSTNAME}:{REDISPORT}, DB: {r.connection_pool.connection_kwargs['db']}")
    print(f"server is running on port {SERVERPORT}")

    server.start()