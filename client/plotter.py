import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

def plot_records(records, plotname="plot"):

    # Extract latency_ms
    latencies = [r["latency_ms"] for r in records if "latency_ms" in r]
    requests = list(range(1, len(latencies)+1))

    avg_latency = np.mean(latencies)
    tail_latency = np.percentile(latencies, 95)

    plt.figure(figsize=(10,5))
    plt.plot(requests, latencies, marker='o', markersize=4, linestyle='-')

    # Draw average line
    plt.axhline(avg_latency, color='green', linestyle='--', label='Average')
    plt.text(len(requests)*0.98, avg_latency - 0.1*avg_latency, f"{avg_latency:.2f} ms", color='green',
             verticalalignment='top', horizontalalignment='right', fontsize=9)

    # Draw p95 line
    plt.axhline(tail_latency, color='red', linestyle='--', label='p95')
    plt.text(len(requests)*0.98, tail_latency + 0.1*tail_latency, f"{tail_latency:.2f} ms", color='red',
             verticalalignment='bottom', horizontalalignment='right', fontsize=9)

    plt.xlabel("Request #")
    plt.ylabel("Latency (ms)")
    plt.title("Request Latencies Over Time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"docs/figs/{plotname}_timeline.png")
    plt.close()

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
    foldername = "docs/run1"
    plotname = "run1"

    records = load_all_json_records(foldername)
    plot_records(records, plotname)