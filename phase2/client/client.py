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

HOSTNAME = "server"
PORT = 5000
TESTING = False

##############################################
# Client Request Logic
#

def make_request(file_ref, keyword, delay=0):
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


##############################################
# Testing logic
#

KEYWORDS = ["bee", "black", "January is the best month of the year", "yellow", "honey", "flower", "buzz", "pollen", "sting", "swarm", 
            "queen", "Barry", "Adam", "Vanessa", "yes", "no", "maybe", "hello", "goodbye"]

KEYWORDS_SHAKESPEARE = ["the", "and", "Roses", "absence", "withering", "Thine eyes", "cheek", "she", "compare", "tyrannous", "good faith", "love", "hate", "night", "day", "sweet", "bitter", "happy", "sad"]


def testing_request(file_ref, keyword):
    try:
        conn = rpyc.connect(HOSTNAME, PORT)
        initial = time.perf_counter_ns()
        result = conn.root.count_words(file_ref, keyword)
        final = time.perf_counter_ns()
        time_taken = final - initial
        logging.info(f"{keyword}::{time_taken}")

    except Exception as e:
        logging.error(f"request failed: {e}")
    finally:
        conn.close() 

def testing():
    # Running a series of requests (the 2nd loop is to test impact of cache!)
    for i in range(2):
        for word in KEYWORDS_SHAKESPEARE:
            testing_request("shakespeare", word)

##############################################



if __name__ == "__main__":        
    if TESTING:
        testing()
    else:
        while True:
            word = random.choice(KEYWORDS_SHAKESPEARE)  # pick a random word 
            make_request("shakespeare", word, delay=random.uniform(0, 5)) # we can add a 3rd arg for delay


