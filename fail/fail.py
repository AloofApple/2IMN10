import time
import subprocess
from datetime import datetime

# Servers to control
SERVERS = ["server2", "server3"]

def log(msg: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def docker_stop(containers):
    log(f"Stopping {', '.join(containers)}")
    subprocess.run(["docker", "stop"] + containers)

def docker_start(containers):
    log(f"Starting {', '.join(containers)}")
    subprocess.run(["docker", "start"] + containers)

if __name__ == "__main__":
    log("Script started")
    time.sleep(1)
    docker_stop(SERVERS)
    docker_start(SERVERS)
    log("Server controller finished")
