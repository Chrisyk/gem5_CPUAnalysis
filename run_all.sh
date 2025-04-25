#!/usr/bin/env bash
set -euo pipefail

GEM5=./build/X86/gem5.opt
SE=configs/deprecated/example/se.py

BIN_DIR=$(pwd)/project/binaries
OUT_DIR=$(pwd)/project/results
mkdir -p "$OUT_DIR"

CPUS_SC=("TimingSimpleCPU" "DerivO3CPU")
L1SIZES=("32" "128")                 # kB
BENCHES_SC=("rand.elf" "sort.elf" "matmul.elf" "dijkstra.elf")
BP_STATIC=("")                       # no flag  (= static)
BP_TAGE=("--bp-type=TAGE")
ITERATIONS="200"
MAX_CYCLES=300000000
########################
# 1.  Single-core sweep
#     Static or TAGE, 32kb or 128 Kb L1, 256 kB L2
########################

######################################
# 2. Dual-core: parallel workloads (T2)
#    static BP, 32 kB L1, 256 kB L2
######################################
CPUS_DC=("TimingSimpleCPU" "DerivO3CPU")
BENCHES_DC=("sort.elf" "matmul.elf" "dijkstra.elf" "rand.elf")

for cpu in "${CPUS_DC[@]}"; do
  for bin in "${BENCHES_DC[@]}"; do
    base=${bin%.elf}
    RUN_DIR="$OUT_DIR/dual_${base}_${cpu}_l132_l2256_static"
    mkdir -p "$RUN_DIR"
    echo "→ $RUN_DIR"
    "$GEM5" --outdir="$RUN_DIR" \
      "$SE" -n 2 --caches --l2cache \
      --l1d_size=32kB --l1i_size=32kB --l2_size=256kB \
      --cpu-type="$cpu" \
      --mem-size=8GB \
      --options "$ITERATIONS;$ITERATIONS" \
      -c "$BIN_DIR/$bin;$BIN_DIR/$bin"
  done
done


#####################################################
# 3. Dual‐core: interference dijkstra + sort (T3)
#    static BP, 32 kB L1, 256 kB L2
#####################################################
CPUS_DC=("TimingSimpleCPU" "DerivO3CPU")
L2=256

for cpu in "${CPUS_DC[@]}"; do
  RUN_DIR="$OUT_DIR/dual_interf_${cpu}_l132_l2${L2}_static"
  mkdir -p "$RUN_DIR"
  echo "→ $RUN_DIR"
  "$GEM5" --outdir="$RUN_DIR" \
    "$SE" -n 2 --caches --l2cache \
    --l1d_size=32kB --l1i_size=32kB --l2_size=${L2}kB \
    --cpu-type="$cpu" \
    --mem-size=8GB \
    --options "$ITERATIONS;$ITERATIONS" \
    -c "$BIN_DIR/dijkstra.elf;$BIN_DIR/sort.elf"
done

echo "All simulations submitted."
