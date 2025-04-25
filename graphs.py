#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the data
df = pd.read_csv('results/summary.csv')

# 2. Microarchitecture: 32kb vs 128kb (single 32kb vs 128 kb cache)
df_sc = df[
    (df['core_type'] == 'single') &
    (df['l1_size'].isin([32, 128]))
]

# identify the two CPU types present
cpus = df_sc['cpu_type'].unique()

# set up side-by-side axes
fig, axes = plt.subplots(1, len(cpus), figsize=(10, 4), sharey=True)

for ax, cpu in zip(axes, cpus):
    sub = df_sc[df_sc['cpu_type'] == cpu]
    # pivot: rows=benchmark, cols=L1 size
    pivot = sub.groupby(['benchmark', 'l1_size'])['ipc0'] \
               .mean() \
               .unstack('l1_size')
    pivot.plot(kind='bar', ax=ax, rot=0)
    ax.set_title(f"{cpu.upper()}  (single-core)")
    ax.set_xlabel("Benchmark")
    ax.legend(title="L1 size (kB)")
    
axes[0].set_ylabel("IPC₀")
fig.suptitle("Single-core IPC₀: 32 kB vs 128 kB L1, by CPU")
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()


# 3. L1 Capacity Sensitivity (IPC₀ vs L1 size) per benchmark
for bench in sorted(df['benchmark'].unique()):
    sub = df[df['benchmark'] == bench]
    if sub.empty:
        continue
    plt.figure()
    for (cpu, bp, l2), grp in sub.groupby(['cpu_type','branch_predictor','l2_size']):
        grp = grp.sort_values('l1_size')
        plt.plot(
            grp['l1_size'],
            grp['ipc0'],
            marker='o',
            label=f"{cpu}/{bp}/L2={l2}kB"
        )
    plt.title(f"L1 Size vs IPC0 ({bench})")
    plt.xlabel("L1 size (kB)")
    plt.ylabel("IPC0")
    plt.legend()
    plt.tight_layout()
    plt.show()

# 4. Branch Predictor: Static vs TAGE per CPU type
for cpu in df['cpu_type'].unique():
    sub = df[df['cpu_type'] == cpu]
    pivot = sub.groupby(['benchmark','branch_predictor'])['ipc0'] \
               .mean() \
               .unstack('branch_predictor')
    ax = pivot.plot(kind='bar', rot=0)
    ax.set_title(f"IPC0 by Branch Predictor on {cpu.upper()}")
    ax.set_ylabel("IPC0")
    plt.tight_layout()
    plt.show()

# 5. Multicore: Aggregate IPC (matmul scaling vs interf interference)
dual = df[df['core_type']=='dual'].copy()
dual['agg_ipc'] = dual['ipc0'] + dual['ipc1']
pivot = dual.pivot_table(
    index=['cpu_type','branch_predictor'],
    columns='benchmark',
    values='agg_ipc'
)
ax = pivot[['matmul','interf']].plot(kind='bar', rot=0)
ax.set_title("Aggregate IPC: matmul (scaling) vs interf (interference)")
ax.set_ylabel("Agg IPC")
plt.tight_layout()
plt.show()
