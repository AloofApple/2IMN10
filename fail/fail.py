import time
import subprocess

# Servers to control
SERVERS = ["server2", "server3"]

# Timing in seconds
STOP_AFTER = 1
RESTART_AFTER = 2

def docker_stop(containers):
    print(f"Stopping {', '.join(containers)}")
    subprocess.run(["docker", "stop"] + containers)

def docker_start(containers):
    print(f"Starting {', '.join(containers)}")
    subprocess.run(["docker", "start"] + containers)

if __name__ == "__main__":
    print(f"waiting {STOP_AFTER}s to stop servers")
    time.sleep(STOP_AFTER)
    docker_stop(SERVERS)

    print(f"Waiting {RESTART_AFTER}s before restarting servers")
    time.sleep(RESTART_AFTER)

    docker_start(SERVERS)
    print("Server controller finished")
