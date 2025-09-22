import rpyc
import logging
import time
import socket
import os
import json
from datetime import datetime

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
TESTING = False

KEYWORDS = ["bee", "black", "January is the best month of the year", 
            "yellow", "honey", "flower", "buzz", "pollen", "sting", 
            "swarm", "queen", "Barry", "Adam", "Vanessa", "yes", 
            "no", "maybe", "hello", "goodbye"]

KEYWORDS_SHAKESPEARE = ["the", "and", "Roses", "absence", "withering", 
                        "Thine eyes", "cheek", "she", "compare", "tyrannous", 
                        "good faith", "love", "hate", "night", "day", "sweet", 
                        "bitter", "happy", "sad" ]


############################################################################################################
# Client Request
#

def make_request(file_ref, keyword, delay=2):
    record = None
    try:
        conn = rpyc.connect(HOSTNAME, PORT)
        
        initial = time.perf_counter_ns()
        result = conn.root.count_words(file_ref, keyword)
        final = time.perf_counter_ns()
        time_taken = (final - initial) / 1e6  # ms

        record = {
            "timestamp": datetime.now().isoformat(),
            "latency_ms": time_taken,
            "count": result
        }

        logging.info(
            f"received count={result} for keyword='{keyword}' in fileRef={file_ref} in {time_taken:.2f} ms"
        )

    except Exception as e:
        logging.error(f"request failed: {e}")

    finally:
        conn.close()

    time.sleep(delay)
    return record

# For testing purposes
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


# For making the figures
def simulate_load(file_ref, keywords, delay=0, num_requests=10):
    i = 0
    n = len(keywords)
    records = []

    for _ in range(num_requests):
        word = keywords[i]
        record = make_request(file_ref, word, delay)
        records.append(record)
        i = (i + 1) % n

    return records

def save_records(records, folder="results", filename="latencies.json"):
    os.makedirs(folder, exist_ok=True)
    
    # Full path to the file
    filepath = os.path.join(folder, filename)

    logging.info(f"Saved {len(records)} records to {filepath}")
    # Save JSON
    with open(filepath, "w") as f:
        json.dump(records, f, indent=2)

if __name__ == "__main__":        
    if TESTING:
        testing()
    else:
        # Scenario 50 clients and 10 requests each with no delay 
        foldername = "docs/round_robin2"
        hostname = socket.gethostname()
        records = simulate_load("shakespeare", KEYWORDS_SHAKESPEARE)
        save_records(records, folder=foldername, filename=f"{hostname}_results.json")


