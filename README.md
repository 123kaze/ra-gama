# RA-Gama: repetition-aware memory allocation for learned Bloom filters

**English** | [简体中文](README.md)

This repository contains the code, frozen experiment protocols, logs and results for **RA-PLBF**, whose main method is **RA6**. It extends the model/filter allocation problem studied by Gama (CIKM 2025) with a cache of verified false-positive keys and learning-window repetition statistics.

**Start here:** [latest eight-setting timing report, in English](windows_research/round14_main_e2e_v2/results/report.md) · [full BF+cache baseline coverage](windows_research/round13_complete/results/baseline_report.md) · [reproduction details](REPRODUCING.md)

The entry point and latest timing report are in English; many historical research notes remain in Chinese. This is a **public, non-anonymized research repository**, not a claim of an accepted or artifact-evaluated paper.

## What RA6 does

1. Use the first 25% of a query stream to estimate repetition and predict false positives over the remaining 75%.
2. Search model-tree prefixes and negative-cache memory fractions, with a FastPLBF dynamic-programming allocator for score segments.
3. Build the five leading candidates from the frozen first-stage ranking, then rerank using their actual false-positive bucket loads.

The cache is 4-way set-associative CLOCK. Evaluation starts with an **empty cache**. The no-repeat reduction is to the **shared-engine Gama configuration**, not to an ordinary Bloom filter, and does not imply that RA6 always beats other baselines.

The shared-engine experiments charge packed Bloom-filter storage, executable model arrays, allocated cache bytes and array headers. **The authors' original Gama implementation uses a different accounting scheme** and is reported separately.

## Quick verification: no datasets, third-party checkout or LaTeX required

Clone normally and use Python 3.10+ with only its standard library:

```bash
git clone https://github.com/123kaze/ra-gama.git
cd ra-gama

# Check complete BF/BF+cache coverage, budgets, stream digests and summary arithmetic.
python3 windows_research/round13_complete/src/verify_baselines.py

# Reconstruct and compare the latest eight-setting timing tables from all 72 records.
python3 windows_research/round14_main_e2e_v2/src/report14.py --verify-only
python3 windows_research/round14_main_e2e_v2/src/test_report14.py -v

# Check the earlier URL/COD paired prefix-scoring experiment.
python3 windows_research/round13_complete/src/verify_scoring.py
```

These commands verify **archived results**, not freshly trained models or new timing measurements. The round-14 checker explicitly reports original-source files unavailable in a non-recursive clone; it does not claim to have checked or executed missing upstream code. On the experiment host, `--inputs` additionally requires all frozen source files and hashes the original datasets, CSVs and query fixtures.

For historical round-10/11 tables:

```bash
python3 scripts/reproduce_results.py --table all --output reproduced
```

Those historical TCP-only BF comparisons use the older conservative-header baseline. The stronger physical-accounting baseline is in **rounds 12–13**; do not substitute the old table for the new one.

## A genuine from-scratch smoke test

With the main environment installed, this command generates a fixed synthetic dataset, trains a model, selects/builds filters and executes native queries without downloading research datasets:

```bash
.condaenv/bin/python windows_research/round12_nomodel/src/minimal_e2e.py --output reproduced/e2e.json
```

This is a correctness and executability check, **not performance evidence**. It does not require RA6 to win; its ordinary BF+cache result is retained even when better.

## Latest results and their limits

### Complete ordinary BF+cache controls

Round 13 completes coverage of the original **1,146 cases**, **16 TCP-only settings**, and **4 MAWI-24 settings**, in both verified-prefix and fp64 cache formats: **2,332 aligned cache-specific comparisons**.

- Excluding probe replay leaves 1,076 original-main cases. The pre-existing reference-FP threshold of at least 30 retains 748 cases. Against BF+cache, both formats have **718 wins, 0 ties and 30 losses**.
- All 30 retained losses are fresh-key adversarial workloads: 10 CAIDA and 20 Shalla cases. Low-count results and the 70 probe-replay cases are disclosed separately.
- On **TCP-only**, both formats lose in **13/16 settings**. Median `(FP_RA6+1)/(FP_BFcache+1)` is **1.063** for the indexed format and **1.053** for fp64. This concerns the tested features, membership construction and budgets, not all learned filters on TCP.
- The added MAWI-24 baselines and fp64 runs are **post-hoc supplements**, not a new independent holdout.

Cases share models, datasets and query pools; hundreds of rows are **not hundreds of independent statistical samples**. Probe-replay methods replay their own false positives, so their evaluation tails are not elementwise identical across structures.

### Optimized full construction: the eight main-table settings

Round 14 reruns **original G-PLBF, RA6-loop and RA6-leaf in the same campaign**: eight settings, three repetitions and 72 fresh single-threaded processes, run serially with rotated method order. A separate three-process pilot is excluded.

All **24 RA6 pairs** match in model/14-prefix score digests, selected configuration, filter payloads and native query counts. All three methods reproduce their corresponding round-7 configurations/counts.

| Dataset | Budget (KiB) | Loop/leaf construction speedup | Leaf/original construction cost ratio |
|---|---:|---:|---:|
| CAIDA-flow | 24 | 2.313× | 10.375 |
| URL | 128 | 2.034× | 4.996 |
| MAWI-20 | 24 | 2.095× | 18.514 |
| MAWI-21 | 24 | 1.824× | 14.227 |
| MAWI-22 | 24 | 2.033× | 16.763 |
| CAIDA synthetic | 256 | 2.625× | 3.782 |
| Shalla | 1024 | 2.500× | 0.964 |
| COD | 1024 | 1.712× | 0.828 |

Each ratio is the **median of three paired ratios**, not a ratio of separate medians. A cost ratio below one favors RA6-leaf.

- Relative to RA6-loop, construction improves in all 24 pairs; the eight setting-level speedup medians span **1.71–2.62×**.
- Relative to original G-PLBF, optimized construction still loses in **6/8 settings**. Shalla's slightly favorable median is not uniform: one of its three repetitions is slower. No significance claim is made.
- Construction plus the full negative tail is faster in **7/8 settings**; CAIDA synthetic remains **1.774×** the original's total computation time.
- Whole-process peak-RSS paired medians increase by **2.9–21.7%** relative to the loop implementation across these settings. Chunked leaf IDs avoid a full-dataset leaf matrix, but do not imply lower total memory.
- The query implementation is unchanged. The newly measured query times are **not evidence that prefix-score preparation accelerates service queries**.

`train_to_ready_s` includes training, scoring/preparation, selection and executable-filter construction. It excludes data reading, JIT warm-up, verification, query-input assembly and evaluation queries. `process_wall_s` includes additional work and is not construction time. Construction-plus-tail excludes database, network and backing-store lookup latency.

The earlier round-13 paper-source URL/COD experiment reports **2.36–2.57×** for a different set of 20 combinations and did not remeasure original Gama. Do not substitute its speedups for the eight-setting results above.

### Important methodological boundaries

- RA6's approximately 3% overall advantage over learned-space Replay is **not significant at the 0.05 level in the archived cluster-aware analysis**. Similar effectiveness with cheaper selection is distinct from a universal false-positive improvement.
- The verified-prefix cache needs a sorted member-hash index, **8 bytes/member outside the filter budget**. The fp64 cache does not consult that index during cache operations, but fingerprint collisions can cause false negatives. Finite member checks are not a universal zero-false-negative guarantee; some older experimental loaders still allocate the index.
- Original Gama uses pickle-based model accounting and its own Bloom-filter backend. Nominally equal budgets do not imply equal physical storage. Language, representation and query-engine differences remain even in the new contemporaneous timings.
- The four original real-trace tasks use UDP members and TCP negatives. The separate TCP-only experiment is necessary and cannot be replaced by favorable results on the original construction.
- Round 8 uses public original data sources associated with the Gama paper, **not an exact reconstruction of the authors' unpublished splits**. The unavailable Yelp dataset is not claimed as reproduced.

## Repository map

| Path | Purpose |
|---|---|
| `windows_research/round5_dp/` | Shared FastPLBF DP engine and the main experimental plan |
| `windows_research/round6_bucket/` | Frozen RA6, original main table, holdout and supplementary studies |
| `windows_research/round7_original_e2e/` | Original implementation versus RA6: initial eight-setting end-to-end campaign |
| `windows_research/round8_paper_data/` | Public-source URL/COD comparisons with original G-LBF/G-PLBF |
| `windows_research/round9_eq7/` | Offline finite-window equation correction and prediction-bias diagnostics |
| `windows_research/round10_fpcache/` | fp64 cache and same-format learned-space replay controls |
| `windows_research/round11_tcp/` | TCP-only membership/query construction |
| `windows_research/round12_nomodel/` | Strong no-model controls, exact overhead accounting, cost/deployment audits, from-scratch smoke test |
| `windows_research/round13_complete/` | Complete BF+cache coverage and initial chunked-prefix-scoring validation |
| `windows_research/round14_main_e2e_v2/` | Latest 72-process eight-setting campaign and English timing report |
| `windows_research/round14_main_e2e/` | Preserved first-launch preflight failure; no training process started |
| `original_baselines/` | Original baseline drivers, pinned submodules and patches |
| `learned_adaptive_hybrid/`, `legacy/` | Earlier studies, retained as historical records |
| `environment/`, `data/README.md` | Pinned environments and dataset preparation locations |

Protocols and source hashes are frozen per round. Later work imports or copies earlier code rather than silently editing a measured version. Logs retain local paths and hardware information as provenance.

## Full experiments and environments

The pinned environments target **macOS arm64 / Apple M4 Pro**. Other platforms must resolve compatible packages; identical timings are not expected.

```bash
conda create -p .condaenv --file environment/main.osx-arm64.lock.txt
conda create -p .condaenv_gama --file environment/gama.osx-arm64.lock.txt
.condaenv_gama/bin/python -m pip install -r environment/gama.pip.txt

# Fetch pinned upstream repositories and regenerate local patched files.
scripts/setup_third_party.sh
# Optional: also build the external C/C++ baseline drivers.
# scripts/setup_third_party.sh --no-fetch --build
```

Prepare datasets and round-7 query fixtures using the linked data and round-specific instructions before running the latest campaign. Large datasets are not bundled. The main environment uses conda-forge LightGBM; the authors' original implementation uses its separate Python 3.10 environment.

The full launcher is `windows_research/round14_main_e2e_v2/src/run14.py`. **It is resume-oriented**: completed checked outputs are skipped, and failed/incomplete existing outputs are rejected. An ordinary clone already contains completed outputs; invoking the launcher there is not a fresh rerun. Use a separate experiment copy/output location and preserve the archived results before arranging a new timing campaign. Do not run memory-heavy timing workers concurrently.

## Third-party code and archival status

See [THIRD_PARTY.md](THIRD_PARTY.md). Unlicensed upstream implementations are referenced through pinned submodules and local patches, **not copied into this repository**. Generated adapter files are ignored by Git. BSD-licensed adaptive-filter ports retain their upstream license files. Fetching a submodule does not grant a new license or permission to redistribute it.

No Zenodo DOI is asserted here. A durable archival release needs an authenticated account, confirmed creator metadata and appropriate licensing; this README does not invent any of these.
