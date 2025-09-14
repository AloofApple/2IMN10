import rpyc

HOSTNAME = "loadbalancer"
PORT = 1200

if __name__ == "__main__":
   
    for i in range (6):
        conn = rpyc.connect(HOSTNAME, PORT)
        file_ref = 0
        keyword = "of" 
        result = conn.root.count_words(file_ref, keyword)

        # Print the result
        print(f"\n==== Request {i+1} ====")
        print(f"{'File ref:':<12}{file_ref}")
        print(f"{'Keyword:':<12}{keyword}")
        print(f"{'Word count:':<12}{result}")
        conn.close()