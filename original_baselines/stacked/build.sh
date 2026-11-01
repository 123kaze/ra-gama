#!/bin/bash
# Build the official Stacked Filter driver on arm64 (clang). overlay/ is produced by scripts/setup_third_party.sh.
set -e
cd "$(dirname "$0")"
c++ -O3 -std=c++17 -w -D_GLIBCXX17_INLINE=inline -include cassert \
  -Ioverlay/StackedFilter -Ioverlay/BloomFilter -Ioverlay/Optimization \
  stacked_orig_driver.cpp -o stacked_orig_driver
