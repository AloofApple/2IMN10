import os
import time
import subprocess

# Servers to control
SERVERS = ["server2", "server3"]

# Timing in seconds
STOP_AFTER = 3
RESTART_AFTER = 9

def docker_stop(containers):
    for c in containers:
        print(f"Stopping {c}")
        subprocess.run(["docker", "stop", c])

def docker_start(containers):
    for c in containers:
        print(f"Starting {c}")
        subprocess.run(["docker", "start", c])

if __name__ == "__main__":
    print(f"waiting {STOP_AFTER}s to stop servers")
    time.sleep(STOP_AFTER)
    docker_stop(SERVERS)

    print(f"Waiting {RESTART_AFTER}s before restarting servers")
    time.sleep(RESTART_AFTER)

    docker_start(SERVERS)
    print("Chaos controller finished")
