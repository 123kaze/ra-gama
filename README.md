# RA-Gama：面向重复查询的学习型 Bloom 过滤器内存分配

本仓库是 RA-PLBF（主方法 RA6）的全部代码、实验记录和结果。它在 Gama（CIKM'25，学习型 Bloom 过滤器的模型/过滤器内存分配）之上，把查询流里的重复也算进分配：

- 在模型树数 × 负例缓存比例的候选中，用学习期（流的前 25%）统计出的每个 key 的重复率预测评估段的误报；
- 按预测结果给 FastPLBF 的分段重新加权，并给一个缓存已验证误报 key 的 4 路 CLOCK 缓存分配空间；
- RA6 在 RA4 的前 5 个候选上，按实际桶负载重新精算后再选。没有重复时，它与 Gama 逐位相同。

所有对比使用相同的查询流，并按物理字节记账（打包 BF、可执行模型数组、缓存实际分配和数组头）。

## 目录

| 目录 | 内容 |
|---|---|
| `learned_adaptive_hybrid/` | 最早的 Mac 端项目（实验 1–14），"Gama＋缓存"的问题定义、决策记录和全部结论。见其 `README.md`、`docs/` |
| `windows_research/` | 之后严格记账、逐轮冻结的研究，每一轮一个目录，后一轮只导入前一轮的代码、不修改它 |
| `windows_research/round2_backlog/` | 共享引擎 `src/engine.py`，以及第二轮的全部任务 |
| `windows_research/round3_ra_plbf/` – `round4_ra_plbf/` | 方法 C（RA-PLBF）及其根因修正、消融、MAWI 2023 留出集 |
| `windows_research/round5_dp/` | FastPLBF 动态规划分配器，以及 E1–E13 实验计划和结果 |
| `windows_research/round6_bucket/` | **主方法 RA6**、MAWI 2024 留出集，E3–E12 和全部补充实验。**结果总览：`results/总览.md`** |
| `windows_research/round7_original_e2e/` | 作者原版 G-PLBF 与 RA6 从训练、构建到实际查询的端到端实测（8 个设置 × 3 次） |
| `windows_research/round8_paper_data/` | 按 Gama 论文公开的原始数据源（URL、COD）重新评估原版 G-LBF、G-PLBF 与 RA6 |
| `windows_research/round9_eq7/` | 离线诊断：给 RA6 的每 key 缺失公式（论文式 7）加上有限窗口修正后，预测偏差和配置选择会变多少（方法不变） |
| `original_baselines/` | 用各论文官方代码重跑的对照：Gama、FastPLBF、Stacked Filter、AdaptiveQF、SkiQF。见其 `README.md`、`结论.md` |
| `legacy/` | 更早的"LightTree-PLBF 学生 vs Gama 教师"研究（`做了什么..md`、`实验结果.md`），只作存档 |
| `environment/` | 两个 conda 环境的精确包列表 |
| `data/README.md` | 每个数据集放在哪里、从哪里下载 |
| `scripts/setup_third_party.sh` | 取回子模块并生成打过补丁的第三方文件，可选编译 C/C++ 驱动 |

每一轮的方法冻结记录在 `plan/design-freeze.md` 和 `plan/freeze.json`（含代码哈希）。冻结轮次的代码不要修改，有改动就复制到新一轮。

## 环境

```bash
git clone --recursive git@github.com:123kaze/ra-gama.git && cd ra-gama
# 主环境：Python 3.12 + numpy/pandas/lightgbm/numba（conda-forge）
conda create -p .condaenv --file environment/main.osx-arm64.lock.txt
# 运行作者 Gama 原版代码用的 Python 3.10 环境
conda create -p .condaenv_gama --file environment/gama.osx-arm64.lock.txt
.condaenv_gama/bin/python -m pip install -r environment/gama.pip.txt
# 生成打补丁的第三方文件，并编译原版 Stacked / AQF / SkiQF 驱动
scripts/setup_third_party.sh --no-fetch --build
```

- 包列表是在 macOS arm64（Apple M4 Pro）上导出的。其他平台要按包名和版本号重新解析。pip 版 lightgbm 在 Mac 上缺 libomp，所以主环境全部用 conda-forge。
- How-to-Train-Your-Filter 子模块约 1.1 GB，只有 `learned_adaptive_hybrid` 的 Caida/Shalla 数据和 AQF/Stacked 驱动需要它。
- 数据集不在仓库里，按 `data/README.md` 准备。
- 没有统一的测试集。正确性检查写在实验里：每个结构都断言零假阴性和不超预算；重构必须逐行复现之前的结果。轮次目录里的 `test_*.py` 是少量单元检查。

## 怎么跑

各轮的脚本要在本轮目录下运行，并互相作为普通模块导入：

```bash
cd learned_adaptive_hybrid && ../.condaenv/bin/python -u src/exp13_deployable.py --dataset caida_flow   # 最快的冒烟测试，约 20 秒
cd windows_research/round6_bucket && ../../.condaenv/bin/python -u src/run6.py --dataset cod --budgets 256,1024,4096 && ../../.condaenv/bin/python src/report6.py
cd windows_research/round7_original_e2e && ../../.condaenv/bin/python -u src/run.py --reps 3
cd windows_research/round8_paper_data && ../../.condaenv/bin/python -u src/run.py
```

更多命令见各目录的 `README.md` 和 `CLAUDE.md`。长时间计时实验要在空闲机器上串行跑。

## 结果从哪里看

- **全部实验的一页总览和已知弱点：** `windows_research/round6_bucket/results/总览.md`
- 主表（30 个设置、1146 个案例）：`windows_research/round6_bucket/results/report.md`
- 独立留出集 MAWI 2024：`windows_research/round6_bucket/results/holdout/结论.md`
- 扩展性、系统开销、敏感性与漂移、统计检验：同目录的 `e5_report.md`、`e789_report.md`、`e10_e11_report.md`、`e12_stats.md`；构建时间：`round5_dp/results/e4_report.md`
- learned stacked 对照与 RA6-warm：`round6_bucket/results/stacked_结论.md`
- 原版代码基线：`original_baselines/结论.md`；RA6 对作者原版 Gama 的误报对比：`round6_bucket/results/ra6_vs_gama_original.md`
- 原版 G-PLBF 与 RA6 的端到端实测：`round7_original_e2e/results/结论.md`
- 论文公开数据源上的重新评估（URL、COD × 5 个预算 × 3 次，90/90 成功）：`round8_paper_data/results/结论.md`、`report.md`、`data_availability.md`
- 式 (7) 有限窗口修正的离线诊断：`round9_eq7/results/结论.md`

## 结果的使用边界

总览里列了全部需要如实写的弱点，主要的几条是：

- RA6 对网格回放整体约好 3%，按簇检验在 0.05 水平上不显著。
- 缓存插入要查询成员哈希索引，这份索引不在过滤器预算内。
- 相对作者原版代码，RA6 误报更少，但从头构建更慢；速度差异里包含实现语言和内存表示的差别。
- 原版代码的预算口径（pickle 计模型大小、BF 后端实际容量）与 RA6 的物理记账不同。

结果文件和日志里有运行时的本机绝对路径和硬件信息，这些都按原样保留，作为运行记录。

## 第三方代码

见 `THIRD_PARTY.md`。未声明许可的上游代码只以子模块和补丁的形式出现，不在本仓库里转发。
