import os
import rpyc
import time

PORT = 18861

if __name__ == "__main__":
    conn = rpyc.connect("server", PORT)

    for i in range (3):
        text = "Hello world!"
        keyword = "Hello" 
        result = conn.root.count_words(text, keyword)

        # Print the result
        print(f"Request: {i+1}", flush=True)
        print(f"Text: {text}", flush=True)
        print(f"Keyword: {keyword}", flush=True)
        print(f"Word count: {result}", flush=True)

    conn.close()