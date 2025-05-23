#!/usr/bin/env python3
"""
    This gathers the data from the output of the bash script
    and puts it into a csv file.
"""
import re, csv, glob, pathlib
from collections import defaultdict

RX = {
    "sim_sec": r"^simSeconds\s+([\d.eE+-]+)",
    "l2miss":  r"^system\.l2\.overall[Mm]isses::total\s+(\d+)",
    "l2hit":   r"^system\.l2\.overall[Hh]its::total\s+(\d+)",
}

for c in (0, 1):
    core = r"(?:cpu|cpu0|cpu\.?)" if c == 0 else r"cpu1"
    RX.update({
        f"ipc{c}":    fr"^system\.{core}\.ipc\s+([\d.eE+-]+)",
        f"l1miss{c}": fr"^system\.{core}\.dcache\.overall[Mm]isses::total\s+(\d+)",
        f"l1hit{c}":  fr"^system\.{core}\.dcache\.overall[Hh]its::total\s+(\d+)",
        f"inst{c}":   fr"^system\.{core}\.commitStats0\.numInsts\s+(\d+)",
        f"bpmiss{c}": fr"^system\.{core}\.branchPred\.condIncorrect\s+(\d+)",
        f"bppred{c}": fr"^system\.{core}\.branchPred\.condPredicted\s+(\d+)",
    })

def parse_stats(path: str) -> dict:
    v = defaultdict(lambda: None)
    with open(path) as fh:
        for line in fh:
            for key, rx in RX.items():
                m = re.match(rx, line)
                if m:
                    v[key] = float(m.group(1))
    for c in (0, 1):
        miss = v[f"l1miss{c}"]; hit = v[f"l1hit{c}"]; inst = v[f"inst{c}"]
        if miss is not None and inst:
            v[f"L1_MPKI{c}"] = 1000 * miss / inst
        if hit is not None and miss is not None:
            v[f"L1_miss{c}%"] = 100 * miss / (hit + miss)
        bp_pred = v[f"bppred{c}"]; bp_miss = v[f"bpmiss{c}"]
        if bp_pred:
            v[f"BP_miss{c}%"] = 100 * bp_miss / bp_pred
    if v["l2hit"] is not None and v["l2miss"] is not None:
        v["L2_miss%"] = 100 * v["l2miss"] / (v["l2hit"] + v["l2miss"])

    label = pathlib.Path(path).parent.name
    v["label"] = label

    v["core_type"] = "dual" if "dual" in label else "single"
    v["benchmark"] = next((x for x in ["matmul", "dijkstra", "sort", "interf", "rand"] if x in label), None)
    v["cpu_type"] = next((x for x in ["DerivO3CPU", "TimingSimpleCPU", "o3", "timing"] if x in label), None)
    v["branch_predictor"] = "TAGE" if "TAGE" in label else "static"

    l1_match = re.search(r"_l1(\d+)", label)
    l2_match = re.search(r"_l2(\d+)", label)
    v["l1_size"] = l1_match.group(1) if l1_match else None
    v["l2_size"] = l2_match.group(1) if l2_match else None

    return v

rows = [parse_stats(p) for p in glob.glob("project/results/*/stats.txt")]
rows.sort(key=lambda r: r["label"])

cols = ["label", "core_type", "benchmark", "cpu_type", "branch_predictor", "l1_size", "l2_size",
        "ipc0", "ipc1", "sim_sec", "L1_MPKI0", "L1_MPKI1",
        "L1_miss0%", "L1_miss1%", "L2_miss%", "BP_miss0%", "BP_miss1%"]

out_csv = pathlib.Path("summary.csv")
with out_csv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {out_csv}  ({len(rows)} runs)")
