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
    plt.plot(requests, latencies, color="blue", linestyle="-", linewidth=2)

    # --- Separate cache hits and misses ---
    hit_x, hit_y = [], []
    miss_x, miss_y = [], []
    for i, r in enumerate(records, start=1):
        if "latency_ms" not in r:
            continue
        if r.get("cache_miss", False):
            miss_x.append(i)
            miss_y.append(r["latency_ms"])
        else:
            hit_x.append(i)
            hit_y.append(r["latency_ms"])

    # Overlay points with different colors
    plt.scatter(hit_x, hit_y, color="blue", s=40, label="Cache Hit", zorder=5)
    plt.scatter(miss_x, miss_y, color="red", s=40, label="Cache Miss", zorder=5)

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
    plt.title(f"{plotname}\nThroughput: {throughput:.2f} req/sec")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"docs/figs/{plotname}_timeline.png")
    plt.close()

def load_all_json_records(folders):
    """
    Load JSON records from a single folder or a list of folders,
    then compute the average latency and count per request index across folders,
    and preserve cache_miss as True if any experiment had True.
    
    Returns:
        List of dicts with averaged values per point:
        [{"timestamp": ..., "latency_ms": ..., "count": ..., "cache_miss": ..., "keyword": ...}, ...]
    """
    if isinstance(folders, str):
        folders = [folders]

    # Load all records for each folder separately
    folders_records = []
    for folder in folders:
        all_records = []
        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                path = os.path.join(folder, filename)
                with open(path, "r") as f:
                    records = json.load(f)
                    all_records.extend([r for r in records if r is not None])
        # Sort by timestamp to maintain order
        all_records.sort(key=lambda r: datetime.fromisoformat(r["timestamp"]))
        folders_records.append(all_records)

    # Assume all experiments have the same number of points
    num_points = 20 # len(folders_records[0])

    averaged_records = []
    for i in range(num_points):
        latencies = [folder[i]["latency_ms"] for folder in folders_records]
        counts = [folder[i]["count"] for folder in folders_records]
        cache_misses = [folder[i]["cache_miss"] for folder in folders_records]

        avg_record = {
            "timestamp": folders_records[0][i]["timestamp"],
            "latency_ms": float(np.mean(latencies)),
            "count": int(np.mean(counts)),
            "cache_miss": any(cache_misses),
            "keyword": folders_records[0][i]["keyword"]
        }
        averaged_records.append(avg_record)

    return averaged_records

if __name__ == "__main__":
    foldername = "docs/round_robin/run1fails"
    plotname = "Request Latencies Over Time - round_robin"

    records = load_all_json_records(foldername)
    plot_records(records, plotname)