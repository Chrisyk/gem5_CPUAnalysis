#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

df = pd.read_csv('summary.csv')

plot_dir = Path('plots')
plot_dir.mkdir(exist_ok=True)

def save(fig, name):
    fig.tight_layout()
    fig.savefig(plot_dir / name, dpi=180)
    plt.close(fig)

# 2.0 Microarchitecture: In-order vs. Out-of-order (IPC)
sc = df[
    (df['core_type'] == 'single') &
    (df['branch_predictor'] == 'static') &
    (df['l1_size'] == 32) &
    (df['l2_size'] == 256)
]
workloads = ['dijkstra', 'matmul', 'sort', 'rand']
workload_labels = ['Dijkstra', 'Matrix Multiplication', 'Bubble Sort', 'Random-bit Branch']
cpu_map = {'DerivO3CPU': 'O3', 'TimingSimpleCPU': 'Tim'}

x = range(len(workloads))
width = 0.35
fig, ax = plt.subplots(figsize=(8, 4))
for i, cpu in enumerate(['DerivO3CPU', 'TimingSimpleCPU']):
    vals = [sc[(sc['cpu_type'] == cpu) & (sc['benchmark'] == wl)]['ipc0'].iloc[0] for wl in workloads]
    pos = [xi - width/2 + i*width for xi in x]
    ax.bar(pos, vals, width, label=cpu_map[cpu])
ax.set_xticks(x)
ax.set_xticklabels(workload_labels, rotation=45, ha='right')
ax.set_title('Single-Core IPC: O3 vs Tim (Static BP, 32 KB L1, 256 KB L2)')
ax.set_ylabel('IPC')
ax.legend()
save(fig, 'single_core_ipc.png')

# 2.1 Cache Sensitivity: L1 MPKI
for cpu in df['cpu_type'].unique():
    sub = df[(df['core_type'] == 'single') & (df['cpu_type'] == cpu)]
    fig, ax = plt.subplots(figsize=(8, 4))
    for size in sorted(sub['l1_size'].unique()):
        d = sub[sub['l1_size'] == size]
        ax.bar(d['benchmark'], d['L1_MPKI0'], label=f'{size} kB')
    ax.set_title(f'L1 MPKI: {", ".join(map(str, sorted(sub["l1_size"].unique())))} kB ({cpu})')
    ax.set_ylabel('MPKI')
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    save(fig, f'cache_sensitivity_mpki_{cpu}.png')

# 2.2 Branch Prediction (DerivO3CPU only)
bp = df[
    (df['core_type'] == 'single') &
    (df['cpu_type'] == 'DerivO3CPU') &
    (df['branch_predictor'].isin(['static', 'TAGE']))
]
fig, ax = plt.subplots(figsize=(8, 4))
for pred in ['static', 'TAGE']:
    d = bp[bp['branch_predictor'] == pred]
    ax.bar(d['benchmark'], d['BP_miss0%'], label=pred)
ax.set_title('Branch-Mispredict %: Static vs TAGE (DerivO3CPU)')
ax.set_ylabel('Mispredict %')
ax.legend()
ax.tick_params(axis='x', rotation=45)
save(fig, 'branch_mispredict.png')

# 3.0 Dual-Core Scaling (MatMul)
dual = df[(df['core_type'] == 'dual') & (df['benchmark'] == 'matmul')]
fig, ax = plt.subplots(figsize=(8, 4))
x = range(len(dual))
ax.bar([i - 0.2 for i in x], dual['ipc0'], width=0.4, label='Core 0')
ax.bar([i + 0.2 for i in x], dual['ipc1'], width=0.4, label='Core 1')
ax.set_xticks(x)
ax.set_xticklabels(dual['cpu_type'])  
ax.set_title('Dual-Core IPC per Core (MatMul)')
ax.set_ylabel('IPC')
ax.legend()
ax.tick_params(axis='x', rotation=45)
save(fig, 'dual_scaling_ipc.png')

# 3.1 Interference (Dijkstra + Sort)
intf = df[(df['core_type'] == 'dual') & (df['benchmark'] == 'interf')]
fig, ax = plt.subplots(figsize=(8, 4))
x = range(len(intf))
ax.bar([i - 0.2 for i in x], intf['ipc0'], width=0.4, label='Core 0')
ax.bar([i + 0.2 for i in x], intf['ipc1'], width=0.4, label='Core 1')
ax.set_xticks(x)
ax.set_xticklabels(intf['cpu_type'])
ax.set_title('Interference IPC per Core (Dijkstra + Sort)')
ax.set_ylabel('IPC')
ax.legend()
ax.tick_params(axis='x', rotation=45)
save(fig, 'interference_ipc.png')

print("All comparison plots saved under plots")
