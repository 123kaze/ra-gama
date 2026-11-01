#!/bin/bash
# Build the AQF and Stacked drivers used by learned_adaptive_hybrid (exp10, exp11, validate_aqf).
# Sources are produced by scripts/setup_third_party.sh; the AQF driver links OpenSSL from ../../.condaenv.
set -e
cd "$(dirname "$0")"
ENV=$(cd ../.. && pwd)/.condaenv
(cd stacked_port
 S=../How-to-Train-Your-Filter/adaptiveqf/external/StackedFilters
 c++ -O3 -std=c++17 -w -include cassert -Ipatch -Ipatch/StackedFilter -I$S/wrapper -I$S/include/StackedFilter \
   -I$S/include/BloomFilter -I$S/include/Optimization stacked_driver.cpp $S/wrapper/stacked_wrapper.cpp -o stacked_driver)
(cd aqf_port
 cc -O3 -DNDEBUG -std=gnu11 -w -Wno-error=int-conversion -Wno-error=incompatible-function-pointer-types \
   -Wno-error=implicit-function-declaration '-Dposix_fallocate(fd,off,len)=ftruncate((fd),(off)+(len))' \
   -I. -Iinclude -I$ENV/include aqf_driver.c src/{gqf,gqf_file,hashutil,partitioned_counter,exp_utility,rand_util,ll_table}.c \
   -L$ENV/lib -lcrypto -lssl -lpthread -lm -Wl,-rpath,$ENV/lib -o aqf_driver)
