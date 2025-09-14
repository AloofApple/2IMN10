import rpyc
import logging
import time

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

def make_request(file_ref, keyword):
    try:
        conn = rpyc.connect(HOSTNAME, PORT)
        file_ref = 0
        keyword = "of"
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
        logging.error(f"request {i+1} failed: {e}")

    finally:
        conn.close()

    # Slight delay between requests
    time.sleep(1)


if __name__ == "__main__":
    for i in range (6):
        make_request(0, "of")
