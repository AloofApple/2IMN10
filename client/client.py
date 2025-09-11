import rpyc

HOSTNAME = "server1" #loadbalancer"
PORT = 5000 #1200

if __name__ == "__main__":
    conn = rpyc.connect(HOSTNAME, PORT)

    for i in range (2):
        file_ref = 0
        keyword = "of" 
        result = conn.root.count_words(file_ref, keyword)

        # Print the result
        print(f"Request: {i+1}")
        print(f"File_ref: {file_ref}")
        print(f"Keyword: {keyword}")
        print(f"Word count: {result}")

    conn.close()