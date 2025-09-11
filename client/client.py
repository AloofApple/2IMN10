import rpyc

HOSTNAME = "server"
SERVERPORT = 5000

if __name__ == "__main__":
    conn = rpyc.connect(HOSTNAME, SERVERPORT)

    for i in range (3):
        text = "Hello Hello world!"
        keyword = "Hello" 
        result = conn.root.count_words(text, keyword)

        # Print the result
        print(f"Request: {i+1}")
        print(f"Text: {text}")
        print(f"Keyword: {keyword}")
        print(f"Word count: {result}")

    conn.close()