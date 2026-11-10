# RA-Gama：面向重复查询的学习型 Bloom 过滤器内存分配

[English README](README.en.md) | 简体中文

本仓库是 RA-PLBF（主方法 RA6）的全部代码、实验记录和结果。它在 Gama（CIKM'25，学习型 Bloom 过滤器的模型/过滤器内存分配）之上，把查询流里的重复也算进分配：

- 在模型树数 × 负例缓存比例的候选中，用学习期（流的前 25%）统计出的每个 key 的重复率预测评估段的误报；
- 按预测结果给 FastPLBF 的分段重新加权，并给一个缓存已验证误报 key 的 4 路 CLOCK 缓存分配空间；
- RA6 在 RA4 的前 5 个候选上，按实际桶负载重新精算后再选。没有重复时，它与 Gama 逐位相同。

共享实现的主表使用对齐的查询流，并按物理字节记账（打包 BF、可执行模型数组、缓存实际分配和数组头）；作者原版 Gama 的记账口径不同，见“结果的使用边界”。

## 最小复现（无需原始数据、子模块或 LaTeX）

普通克隆后，用 Python 3.10+ 标准库即可从已提交 CSV 重新生成 TCP-only 对照表：

```bash
python3 scripts/reproduce_results.py
# 再复现第十轮的同格式网格对照，并保存表格、统计值和输入 SHA-256：
python3 scripts/reproduce_results.py --table all --output reproduced
```

这是**存档结果的统计复现，不是重跑训练与查询**。脚本会检查完整案例集合，遇到漏行、重复行或非法计数会失败，不会只取交集后报成功。环境、输入、预期数值、缓存代码冒烟测试和完整重跑入口见 [REPRODUCING.md](REPRODUCING.md)。

已有主环境时，可以不下载数据，**真正从头生成数据、训练、选择、构建并执行原生查询**：

```bash
.condaenv/bin/python windows_research/round12_nomodel/src/minimal_e2e.py --output reproduced/e2e.json
```

这个固定小例子只验证可运行性和正确性，不是论文性能证据。普通 BF＋缓存的全部数据覆盖见 [第十三轮基线结论](windows_research/round13_complete/results/基线补全结论.md)；完整构建成本与统计勘误见 [第十二轮结论](windows_research/round12_nomodel/results/结论.md)。

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
| `windows_research/round9_eq7/` | 离线诊断：式 (7) 的有限窗口修正对预测和选择的影响；RA6 预测偏高从哪里来（方法不变） |
| `windows_research/round10_fpcache/` | 不用成员索引的 64 位指纹缓存（RA6-fp64）、同格式的网格参照，以及与带索引缓存的差距分解 |
| `windows_research/round11_tcp/` | 协议一致的真实轨迹：成员和负例都是 TCP 流（回应 UDP/TCP 构造的质疑） |
| `windows_research/round12_nomodel/` | COD/URL/Shalla 普通 BF＋缓存强基线、TCP-only 精确开销对照、完整构建成本和部署/统计核验；含从头运行的最小入口 |
| `windows_research/round13_complete/` | BF＋缓存全覆盖；pred_leaf 60 次构建／30 对等价核验完成，配对加速中位 2.36–2.57×（见本轮最终结论） |
| `windows_research/round14_main_e2e_v2/` | 主表八设置72进程同期重测原版与新旧RA6；[英文完整表格](windows_research/round14_main_e2e_v2/results/report.md) |
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
- 正确性检查主要写在实验里：带索引结构检查成员不被拒绝以及不超预算；指纹缓存版只记录有限输入下的成员检查，不能据此保证严格零假阴性。轮次目录里有 `test_*.py`；最小复现入口另有标准库回归测试，见 [REPRODUCING.md](REPRODUCING.md)。

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
- 式 (7) 有限窗口修正、预测偏高的来源：`round9_eq7/results/结论.md`、`bias_split.md`
- 不用成员索引的指纹缓存：`round10_fpcache/results/结论.md`、`report.md`
- 协议一致（只用 TCP）的真实轨迹：`round11_tcp/results/结论.md`、`report.md`
- **最新无模型强基线与审计：** [round12 结论](windows_research/round12_nomodel/results/结论.md)、[完整对照](windows_research/round12_nomodel/results/report.md)、[构建成本](windows_research/round12_nomodel/results/construction_cost.md)、[部署及特征统计勘误](windows_research/round12_nomodel/results/deployment_audit.md)

- **全覆盖 BF＋缓存对照（原主表＋TCP-only＋MAWI-24）：** [round13 基线结论](windows_research/round13_complete/results/基线补全结论.md)、[完整报告](windows_research/round13_complete/results/baseline_report.md)。存档可用 `python3 windows_research/round13_complete/src/verify_baselines.py` 校验。
- **pred_leaf 正式计时已完成：** [round13 最终结论](windows_research/round13_complete/results/结论.md)、[完整计时表](windows_research/round13_complete/results/scoring_report.md)。60 次构建／30 对等价检查全部通过，20 个组合的配对加速中位为 2.36–2.57×；分数、配置及误报不变。存档可用 `python3 windows_research/round13_complete/src/verify_scoring.py` 校验。

- **最新主表八设置同期计时：** [第十四轮中文结论](windows_research/round14_main_e2e_v2/results/结论.md)、[英文完整表格](windows_research/round14_main_e2e_v2/results/report.md)。72个正式进程成功，24对RA6等价检查通过；相对旧实现构建加速中位1.71–2.62×。与同期原版相比，构建仍有6/8设置较慢，构建＋全尾段在7/8设置更快。

## 结果的使用边界

总览里列了全部需要如实写的弱点，主要的几条是：

- RA6 对网格回放整体约好 3%，按簇检验在 0.05 水平上不显著。
- 对普通 BF＋缓存并非普遍更好：第十三轮补齐所有数据后，原主表 748 个纳入案例中有 30 个全新对抗案例落后（CAIDA 10、Shalla 20）；TCP-only 按纯 BF 实际开销收费后，RA6/对照中位为 1.063，指纹版为 1.053。旧第十一轮的 1.009/1.041 属于保守头开销对照，不能当作最新强基线。MAWI-24 新基线与指纹版均标注为后续补测，不是新的独立验证。
- 带索引缓存插入要查询成员哈希索引，这份索引不在过滤器预算内。64 位指纹版（第十轮）的缓存操作无需此索引，误报中位高约 5%；碰撞可能造成假阴性。存档的约 1e-15 数值来自理想均匀指纹假设下的占用槽位估算，不是全运行期、任意查询的零假阴性保证，也不是整个实验进程的总内存审计。
- 第七／八轮从头构建较慢的历史结果继续保留。第十四轮已同期重测原版：优化后COD、Shalla的构建中位较快，其余6/8设置仍慢3.78–18.51×；Shalla有一次重复仍较慢，不能声称稳定优势。实现语言、查询内核和物理记账差异仍存在。八设置leaf/loop峰值RSS配对中位增加2.9–21.7%，不宣称普遍节省内存。
- 原版代码的预算口径（pickle 计模型大小、BF 后端实际容量）与 RA6 的物理记账不同。

结果文件和日志里有运行时的本机绝对路径和硬件信息，这些都按原样保留，作为运行记录。

## 第三方代码

见 `THIRD_PARTY.md`。未声明许可的上游代码只以子模块和补丁的形式出现，不在本仓库里转发。
