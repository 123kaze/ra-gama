# 第三方代码

对照方法都用论文作者的官方代码重跑。这些仓库以 git 子模块的形式固定在下表的提交上，`git clone --recursive` 或 `scripts/setup_third_party.sh` 会取回原样代码。

| 子模块路径 | 上游 | 提交 | 许可 |
|---|---|---|---|
| `original_baselines/repos/Spatio-Temporal-Lab__LBF-Gama` | Gama（CIKM'25）github.com/Spatio-Temporal-Lab/LBF-Gama | `27a454a` | 仓库未声明许可 |
| `original_baselines/repos/HarvardDASlab__stackedfilters` | Stacked Filters（VLDB'21）bitbucket.org/HarvardDASlab/stackedfilters | `6e04ca6` | 仓库未声明许可 |
| `original_baselines/repos/kapilvaidya24__PLBF` | PLBF（ICLR'21）github.com/kapilvaidya24/PLBF | `7ed767e` | 仓库未声明许可 |
| `original_baselines/repos/atsukisato__FastPLBF` | Fast PLBF github.com/atsukisato/FastPLBF | `9491e7e` | MIT |
| `original_baselines/repos/splatlab__adaptiveqf`、`saltsystemslab__adaptiveqf` | AdaptiveQF（同一提交的两个地址） | `6a6ca59` | BSD-3-Clause |
| `original_baselines/repos/saltsystemslab__SkiRentalAdaptiveQF` | SkiQF / HybridSkiQF（SIGMOD'26） | `28b8b2b` | BSD-3-Clause |
| `original_baselines/repos/djslzx__telescoping-filter` | TAF（ESA'21），只克隆备查，没有用到 | `286a936` | GPL-3.0 |
| `learned_adaptive_hybrid/external/How-to-Train-Your-Filter` | github.com/saltsystemslab/How-to-Train-Your-Filter（约 1.1 GB，含 Caida、Shalla 等数据压缩包） | `c970c34` | 顶层未声明许可 |

## 本仓库里保存的是什么

- **未声明许可的代码不在本仓库里转发。** 我们对它们的改动只以补丁形式保存，`scripts/setup_third_party.sh` 从子模块复制原文件、打上补丁，生成本地副本（这些生成文件已在 `.gitignore` 中）：
  - `original_baselines/gama/adapter.patch` → `original_baselines/gama/run_gama_plbf_ada.py`：官方 `lgb_url_GamaPLBF_ada.py` 只改了输入路径、预算列表、不可行预算的记录和结果输出，搜索逻辑不变。生成文件的 SHA256 与实验结果里记录的 `source_sha256` 一致（`353e6dd0…`）。
  - `original_baselines/stacked/port.patch` + `stubs/` → `original_baselines/stacked/overlay/`：macOS/clang 移植，`std::min<size_t>`，去掉没用到的商过滤器层和 Cuckoo 层（换成两个空桩头文件）。
  - `learned_adaptive_hybrid/external/stacked_port/StackedFilter.h.patch`、`aqf_port/{gqf.c,partitioned_counter.c}.patch` → 这两个驱动用到的 How-to-Train-Your-Filter 文件。
- **BSD-3-Clause 的 AdaptiveQF / SkiQF 改动副本**（`original_baselines/aqf/port/`、`original_baselines/skiqf/port/`、`original_baselines/skiqf/overlay/`）直接保存，每个目录都附了上游的 `LICENSE`。改动见同目录的 `port.patch`（arm64：popcnt/bsr 换成内建函数，替换 rdtsc、sysinfo、sched_getcpu）。
- 驱动程序 `*_driver.c(pp)`、运行脚本、补丁和空桩是我们写的。

## 验证

整理时在一个全新目录里从这些子模块提交重新生成，47 个生成文件与原来实验时使用的文件逐字节相同，5 个驱动（`stacked_orig_driver`、`aqf_orig_driver`、`skiqf_orig_driver`、`aqf_driver`、`stacked_driver`）都能编译，二进制大小与原来一致。
