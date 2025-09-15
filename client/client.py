import rpyc
import logging
import time
import random

############################################################################################################
# Setup
#

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S"
)

HOSTNAME = "loadbalancer"
PORT = 1200


############################################################################################################
# Client Request
#

def make_request(file_ref, keyword, delay=2):
    try:
        conn = rpyc.connect(HOSTNAME, PORT)
        logging.info(
            f"request keyword='{keyword}' in fileRef={file_ref}"
        )
        result = conn.root.count_words(file_ref, keyword)
        # client_addr  = conn._channel.stream.sock.getsockname()

        # Log the result
        logging.info(
            f"received count={result} for keyword='{keyword}' in fileRef={file_ref}"
        )

    except Exception as e:
        logging.error(f"request failed: {e}")

    finally:
        conn.close()

    # Slight delay between requests
    time.sleep(delay)

KEYWORDS = ["bee", "black", "yellow", "honey", "flower", "buzz", "pollen", "sting", "swarm", 
            "queen", "Barry", "Adam", "Vanessa", "yes", "no", "maybe", "hello", "goodbye"]

if __name__ == "__main__":
    while True:
        word = random.choice(KEYWORDS)  # pick a random word
        make_request("bee_movie", word)
        time.sleep(random.uniform(0, 5))  # wait a bit before next request
