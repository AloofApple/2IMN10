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

KEYWORDS = ["bee", "black", "January is the best month of the year", 
            "yellow", "honey", "flower", "buzz", "pollen", "sting", 
            "swarm", "queen", "Barry", "Adam", "Vanessa", "yes", 
            "no", "maybe", "hello", "goodbye"]

KEYWORDS_SHAKESPEARE = ["the", "and", "Roses", "absence", "withering", 
                        "Thine eyes", "cheek", "she", "compare", "tyrannous", 
                        "good faith", "love", "hate", "night", "day", "sweet", 
                        "bitter", "happy", "sad", "joy"]

# KEYWORDS_SHAKESPEARE = KEYWORDS_SHAKESPEARE[0:10]

############################################################################################################
# Client Request
#

def make_request(file_ref, keyword, delay=0):
    record = None
    timestamp = datetime.now().isoformat()  
    initial = time.perf_counter_ns()

    for attempt in range(2):  # try up to 2 times
        conn = None
    try:
            conn = rpyc.connect(HOSTNAME, PORT)
            result, cache_miss = conn.root.count_words(file_ref, keyword)
            final = time.perf_counter_ns()
            time_taken = (final - initial) / 1e6  # ms

            record = {
                "timestamp": timestamp,
                "latency_ms": time_taken,
                "count": result,
                "cache_miss": cache_miss,
                "keyword": keyword,
            }

            logging.info(
                f"received count={result} for keyword='{keyword}' in fileRef={file_ref} "
                f"in {time_taken:.2f} ms (attempt {attempt + 1})"
            )

            conn.close()
            break 

        except Exception as e:
            logging.warning(f"attempt failed for keyword='{keyword}' ⚠️")

    finally:
        if conn:
            conn.close()

    time.sleep(delay)
    return record

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
    # Scenario 50 clients and 10 requests each with no delay 
    foldername = "/client/docs/least_connections/run4"
    hostname = socket.gethostname()
    records = simulate_load("shakespeare", KEYWORDS_SHAKESPEARE, num_requests=10, delay=0)
    save_records(records, folder=foldername, filename=f"{hostname}_results.json")


