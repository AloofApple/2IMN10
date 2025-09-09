import os
import rpyc

PORT = 18861

if __name__ == "__main__":
    conn = rpyc.connect("server", PORT)

    text = "Hello world!"
    result = conn.root.count_words(text)

    # Print the result
    print(f"Text: {text}")
    print(f"Word count: {result}")

    conn.close()