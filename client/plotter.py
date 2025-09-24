import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

def plot_records(records, plotname="plot"):
    # Extract latency_ms and timestamps
    latencies = [r["latency_ms"] for r in records if "latency_ms" in r]
    timestamps = [datetime.fromisoformat(r["timestamp"]) for r in records if "latency_ms" in r]

    requests = list(range(1, len(latencies)+1))
    avg_latency = np.mean(latencies)
    tail_latency = np.percentile(latencies, 95)

    # Calculate throughput
    duration_sec = (timestamps[-1] - timestamps[0]).total_seconds()
    throughput = len(latencies) / duration_sec

    plt.figure(figsize=(10,5))
    plt.plot(requests, latencies, marker='o', markersize=4, linestyle='-', label="Latencies")

    # --- Mark cache misses with red crosses ---
    miss_requests = []
    miss_latencies = []
    for i, r in enumerate(records, start=1):
        if r.get("cache_miss", False):  # boolean flag
            miss_requests.append(i)
            miss_latencies.append(r["latency_ms"])

    cache_miss_count = len(miss_requests)  # total number of cache misses

    if miss_requests:
        plt.scatter(miss_requests, miss_latencies, marker='x', color='red',
                    s=70, label="Cache Misses", zorder=5)

    # Draw average line
    plt.axhline(avg_latency, color='green', linestyle='--', label='Average')
    plt.text(0.98*len(requests), avg_latency, f"{avg_latency:.2f} ms", color='green',
             verticalalignment='bottom', horizontalalignment='right', fontsize=9)

    # Draw p95 line
    plt.axhline(tail_latency, color='red', linestyle='--', label='p95')
    plt.text(0.98*len(requests), tail_latency, f"{tail_latency:.2f} ms", color='red',
             verticalalignment='bottom', horizontalalignment='right', fontsize=9)

    plt.xlabel("Request Number")
    plt.ylabel("Latency (ms)")
    plt.title(f"{plotname}\nThroughput: {throughput:.2f} req/sec, Cache Misses: {cache_miss_count}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"docs/figs/{plotname}_timeline.png")
    plt.close()

    print(f"Total cache misses: {cache_miss_count}")



def load_all_json_records(folder="docs"):
    all_records = []

    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            path = os.path.join(folder, filename)
            with open(path, "r") as f:
                records = json.load(f)
                all_records.extend(records)  # cleaner than looping

    # Sort by timestamp
    all_records.sort(key=lambda r: datetime.fromisoformat(r["timestamp"]))

    return all_records

if __name__ == "__main__":
    foldername = "docs/least_connections/run1"
    plotname = "Request Latencies Over Time - least_connections"

    records = load_all_json_records(foldername)
    plot_records(records, plotname)