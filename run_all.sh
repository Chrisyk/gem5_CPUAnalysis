#!/usr/bin/env bash
set -euo pipefail

GEM5=./build/X86/gem5.opt
SE=configs/deprecated/example/se.py

BIN_DIR=$(pwd)/project/binaries
OUT_DIR=$(pwd)/project/results
mkdir -p "$OUT_DIR"

CPUS_SC=("TimingSimpleCPU" "DerivO3CPU")
L1SIZES=("32" "128")                 # kB
BENCHES_SC=("sort.elf" "matmul.elf" "dijkstra.elf" "rand.elf")
BP_STATIC=("")                       # no flag  (= static)
BP_TAGE=("--bp-type=TAGE")
ITERATIONS="200"
MAX_CYCLES=300000000
########################
# 1.  Single-core sweep
########################
for cpu in "${CPUS_SC[@]}"; do
  for l1 in "${L1SIZES[@]}"; do
    for bin in "${BENCHES_SC[@]}"; do
      # choose BP list
      bp_flags=("${BP_STATIC[@]}")
      [[ $cpu == DerivO3CPU ]] && bp_flags+=("${BP_TAGE[@]}")

      for bp in "${bp_flags[@]}"; do
        bp_tag=$( [[ -z ${bp} ]] && echo "static" || echo "TAGE")
        RUN_DIR="$OUT_DIR/single_${bin%.elf}_${cpu}_l1${l1}_l2256_${bp_tag}"
        mkdir -p "$RUN_DIR"
        echo "→ $RUN_DIR"
        "$GEM5" --outdir="$RUN_DIR" \
          "$SE" --caches --l2cache \
          --l1d_size=${l1}kB --l1i_size=${l1}kB --l2_size=256kB \
          --cpu-type="$cpu" ${bp:-} \
          -c "$BIN_DIR/$bin"
      done
    done
  done
done


######################################
# 2. Dual-core: parallel matmul (T2)
######################################
CPUS_DC=("TimingSimpleCPU" "DerivO3CPU")
for cpu in "${CPUS_DC[@]}"; do
  for l1 in "${L1SIZES[@]}"; do
    # Always run static; only O3 runs get TAGE
    BP_FLAGS=("")
    [[ $cpu == "DerivO3CPU" ]] && BP_FLAGS+=( "--bp-type=TAGE" )

    for bp in "${BP_FLAGS[@]}"; do
      tag=$([[ -z $bp ]] && echo static || echo TAGE)
      RUN_DIR="$OUT_DIR/dual_matmul_${cpu}_l1${l1}_l2256_${tag}"
      mkdir -p "$RUN_DIR"
      echo "→ $RUN_DIR"
      "$GEM5" --outdir="$RUN_DIR" \
        "$SE" -n 2 --caches --l2cache \
        --l1d_size=${l1}kB --l1i_size=${l1}kB --l2_size=256kB \
        --cpu-type="$cpu" $bp \
        -c "$BIN_DIR/matmul.elf;$BIN_DIR/matmul.elf"
    done
  done
done


#####################################################
# 3. Dual-core: interference dijkstra + sort (T3)
#####################################################
CPUS_DC=("TimingSimpleCPU" "DerivO3CPU")
L2SETS=("256" "1024")

for cpu in "${CPUS_DC[@]}"; do
  for l2 in "${L2SETS[@]}"; do
    BP_FLAGS=("")
    [[ $cpu == "DerivO3CPU" ]] && BP_FLAGS+=( "--bp-type=TAGE" )

    for bp in "${BP_FLAGS[@]}"; do
      tag=$([[ -z $bp ]] && echo static || echo TAGE)
      RUN_DIR="$OUT_DIR/dual_interf_${cpu}_l132_l2${l2}_${tag}"
      mkdir -p "$RUN_DIR"
      echo "→ $RUN_DIR"
      "$GEM5" --outdir="$RUN_DIR" \
        "$SE" -n 2 --caches --l2cache \
        --l1d_size=32kB --l1i_size=32kB --l2_size=${l2}kB \
        --cpu-type="$cpu" $bp \
        -c "$BIN_DIR/dijkstra.elf;$BIN_DIR/sort.elf"
    done
  done
done

echo "All simulations submitted."
