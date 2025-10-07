import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

def plot_records(records, plotname="plot"):
    # Extract latency_ms and timestamps
    latencies = [r["latency_ms"] for r in records if "latency_ms" in r]
    timestamps = [datetime.fromisoformat(r["timestamp"]) for r in records]
    start_time = timestamps[0]
    elapsed_seconds = [(t - start_time).total_seconds() for t in timestamps]

    requests = list(range(1, len(latencies)+1))
    avg_latency = np.mean(latencies)
    tail_latency = np.percentile(latencies, 95)

    plt.figure(figsize=(10,5))
    plt.plot(
        requests, latencies, linestyle="-", linewidth=2, marker="o", markersize=5, label="Latency"
    )

    # Draw average line
    plt.axhline(avg_latency, color='green', linestyle='--', label='Average')
    plt.text(0.98*len(requests), avg_latency, f"{avg_latency:.2f} ms", color='green',
             verticalalignment='bottom', horizontalalignment='right', fontsize=9)

    # Draw p95 line
    plt.axhline(tail_latency, color='red', linestyle='--', label='p95')
    plt.text(0.98*len(requests), tail_latency, f"{tail_latency:.2f} ms", color='red',
             verticalalignment='bottom', horizontalalignment='right', fontsize=9)
    
    for event_time, label, color in [(10, "Stop", "orange"), (20, "Restart", "purple")]:
        # Find closest request index
        closest_idx = min(range(len(elapsed_seconds)), key=lambda i: abs(elapsed_seconds[i]-event_time))
        plt.axvline(requests[closest_idx], color=color, linestyle="--", label=label)

    plt.xlabel("Request Number")
    plt.ylabel("Latency (ms)")
    plt.title(f"{plotname}")
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
    num_points = min(len(folder) for folder in folders_records)

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
    # foldernames = ["docs/round_robin/run1", "docs/round_robin/run2", "docs/round_robin/run3"]
    foldernames = ["docs/least_connections/run1", "docs/least_connections/run2", "docs/least_connections/run3"]
    foldernames = ["docs/least_connections/run1"]
    plotname = "Request Latencies Over Time - Least Connections (50 clients requesting 10 keywords)"

    records = load_all_json_records(foldernames)
    plot_records(records, plotname)