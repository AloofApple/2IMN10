import time
import subprocess
from datetime import datetime

# Servers to control
SERVERS = ["server2"]

def log(msg: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def docker_stop(containers):
    log(f"Stopping {', '.join(containers)}")
    subprocess.run(["docker", "stop", "-t", str(6)] + containers)

def docker_start(containers):
    log(f"Starting {', '.join(containers)}")
    subprocess.run(["docker", "start"] + containers)

if __name__ == "__main__":
    log("Script started")
    docker_stop(SERVERS)
    # time.sleep(0)
    docker_start(SERVERS)
    log("Server controller finished")