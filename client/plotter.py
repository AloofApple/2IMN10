import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime
from adjustText import adjust_text

def plot_records(records, plotname="plot"):
    latencies = [r["latency_ms"] for r in records if "latency_ms" in r]

    requests = list(range(1, len(latencies)+1))
    avg_latency = np.mean(latencies)
    tail_latency = np.percentile(latencies, 95)

    plt.figure(figsize=(8,6))

    # --- Draw the line through all points ---
    plt.plot(
        requests, latencies, linestyle="-", linewidth=2, marker="o", markersize=5, label="Latency"
    )
    plt.xticks(requests)

    # --- Annotate each point with count ---
    texts = []
    
    # --- Create the text objects ---
    for i, r in enumerate(records, start=1):
        if "latency_ms" not in r:
            continue
            
        cnt = r.get("count", "")
        
        # Create the text object at the original point position
        t = plt.text(
            i, r["latency_ms"], 
            str(cnt),
            # rotation=-30,
            va="bottom",
            fontsize=8,
            color="black"
        )
        texts.append(t)
        
    # --- Use adjust_text to move the labels and avoid collision ---
    # The 'arrowprops' draws a line from the label to its original point if it moves far.
    adjust_text(texts, 
                arrowprops=dict(arrowstyle="-", color='lightgray', lw=0.5, shrinkA=5), 
                force_points=(0.2, 0.5))

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
    plt.title(f"{plotname}")
    plt.legend()
    plt.tight_layout()
    os.makedirs("docs/figs", exist_ok=True)
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
    foldernames = ["docs/experiment/run1", "docs/experiment/run2", "docs/experiment/run3"]
    plotname = "Request Latencies Per Request"

    records = load_all_json_records(foldernames)
    plot_records(records, plotname)