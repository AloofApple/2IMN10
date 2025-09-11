import rpyc

HOSTNAME = "server"
SERVERPORT = 5000

if __name__ == "__main__":
    conn = rpyc.connect(HOSTNAME, SERVERPORT)

    for i in range (2):
        filepath = "example.txt"
        keyword = "of" 
        result = conn.root.count_words(filepath, keyword)

        # Print the result
        print(f"Request: {i+1}")
        print(f"Text: {filepath}")
        print(f"Keyword: {keyword}")
        print(f"Word count: {result}")

    conn.close()