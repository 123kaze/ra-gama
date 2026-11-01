#!/usr/bin/env bash
# Fetch the pinned upstream repositories (git submodules) and rebuild the files we derive from them.
#
# Several upstream repositories carry no license (LBF-Gama, Stacked Filters, PLBF,
# How-to-Train-Your-Filter), so this repository does not redistribute their code: it keeps
# only our patches and regenerates the patched copies here. See THIRD_PARTY.md.
#
# usage: scripts/setup_third_party.sh [--no-fetch] [--build]
#   --no-fetch  submodules are already checked out
#   --build     also compile the C/C++ baseline drivers (clang, macOS arm64 tested)
set -euo pipefail
cd "$(dirname "$0")/.."

FETCH=1 BUILD=0
for a in "$@"; do
  case "$a" in
    --no-fetch) FETCH=0 ;;
    --build) BUILD=1 ;;
    *) echo "unknown option $a" >&2; exit 2 ;;
  esac
done
[ $FETCH = 1 ] && git submodule update --init

# patched copy: patch_to <out> <upstream file> <patch>
patch_to() {
  mkdir -p "$(dirname "$1")"
  rm -f "$1"
  patch -s -o "$1" "$2" "$3"
}

# 1. Gama: the official G-PLBF script with input/output adapters (original_baselines/README.md)
G=original_baselines/repos/Spatio-Temporal-Lab__LBF-Gama
patch_to original_baselines/gama/run_gama_plbf_ada.py "$G/lgb_url_GamaPLBF_ada.py" original_baselines/gama/adapter.patch

# 2. Stacked Filters: header overlay = upstream headers + port.patch + stubs for the unused layers
S=original_baselines/repos/HarvardDASlab__stackedfilters/include
O=original_baselines/stacked/overlay
rm -rf "$O"
mkdir -p "$O/BloomFilter" "$O/Optimization" "$O/StackedFilter"
cp "$S/BloomFilter/BloomFilterLayer.h" "$O/BloomFilter/"
for f in ASFContinuousOptimizationObject.h ASFContinuousOptimizationRoutines.h ASFDiscreteOptimizationObject.h \
         ASFDiscreteOptimizationRoutines.h ASFUtils.h BloomOptimizationRoutines.h DiscreteOptimizationRoutines.h \
         OptimizationRoutines.h utils.h workload_generator.h; do
  cp "$S/Optimization/$f" "$O/Optimization/"
done
for f in AdaptiveStackedBF.h CityHash.h Common.h InterfaceAMQ.h InterfaceElement.h ZipfDistribution.h \
         gammafunction.h powerlaw.h; do
  cp "$S/StackedFilter/$f" "$O/StackedFilter/"
done
patch_to "$O/StackedFilter/StackedFilter.h" "$S/StackedFilter/StackedFilter.h" original_baselines/stacked/port.patch
cp -R original_baselines/stacked/stubs/. "$O/"

# 3. learned_adaptive_hybrid/external: AQF and Stacked ports used by exp10/exp11 and validate_aqf
H=learned_adaptive_hybrid/external/How-to-Train-Your-Filter/adaptiveqf
A=learned_adaptive_hybrid/external/aqf_port
HTTYF=1
if [ ! -d "$H/include" ]; then
  HTTYF=0
  echo "How-to-Train-Your-Filter is not checked out (about 1.1 GB): skipping the learned_adaptive_hybrid ports." >&2
  echo "  fetch it with: git submodule update --init learned_adaptive_hybrid/external/How-to-Train-Your-Filter" >&2
fi
if [ $HTTYF = 1 ]; then
mkdir -p "$A/include" "$A/src"
for f in exp_utility.h filter_iface.h gqf.h gqf_file.h gqf_int.h gqf_wrapper.h harness_output.h hashutil.h \
         ll_table.h partitioned_counter.h rand_util.h sglib.h splinter_util.h test_driver.h zipf.h; do
  cp "$H/include/$f" "$A/include/"
done
for f in exp_utility.c gqf_file.c hashutil.c ll_table.c rand_util.c; do
  cp "$H/src/$f" "$A/src/"
done
patch_to "$A/src/gqf.c" "$H/src/gqf.c" "$A/gqf.c.patch"
patch_to "$A/src/partitioned_counter.c" "$H/src/partitioned_counter.c" "$A/partitioned_counter.c.patch"
cp "$H/README.md" "$A/UPSTREAM_README.md"
P=learned_adaptive_hybrid/external/stacked_port
patch_to "$P/patch/StackedFilter/StackedFilter.h" "$H/external/StackedFilters/include/StackedFilter/StackedFilter.h" \
  "$P/StackedFilter.h.patch"
fi

echo "third-party sources ready"

if [ $BUILD = 1 ]; then
  bash original_baselines/aqf/build.sh
  bash original_baselines/skiqf/build.sh
  bash original_baselines/stacked/build.sh
  [ $HTTYF = 1 ] && bash learned_adaptive_hybrid/external/build.sh
  echo "drivers built"
fi
