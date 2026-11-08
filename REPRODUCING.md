# 最小复现入口

本入口只整理既有实验，不修改冻结方法，也不重新挑选参数。

## 1. 一条命令复现一个结果表（不需要下载数据）

环境：**Python 3.10+，仅标准库**。不需要 conda、NumPy、子模块、LaTeX、训练模型或原始网络数据。普通克隆即可，不必 `--recursive`。

```bash
git clone https://github.com/123kaze/ra-gama.git
cd ra-gama
python3 scripts/reproduce_results.py
```

默认重算**第十一轮存档** TCP-only 实验的 16 个设置，打印各方法的误报数和逐案例比值。输入是本仓库已提交的 `windows_research/round11_tcp/results/` CSV，包括普通 BF、BF＋缓存，不仅仅展示相对无缓存 Gama 的收益。

**版本边界：** 下表的 1.009/1.041 是第十一轮保守计入 BF 头开销的结果。第十二轮使用纯 BF 实际数组开销的更强对照，TCP-only 的相应中位数为 **1.063/1.053**，另补齐 COD/URL/Shalla 对照。两轮保留各自结果，不混用。最新报告见 `windows_research/round12_nomodel/results/结论.md`；仅用标准库即可核验完整存档：

```bash
python3 windows_research/round12_nomodel/src/verify_results.py
```

预期主要比值（中位数；计算 `(FP_a+1)/(FP_b+1)` 后取中位）：

| 比较 | 中位 | 不差于参照 |
|---|---:|---:|
| RA6 / 共享实现 Gama | 0.416 | 16/16 |
| RA6 / Replay | 0.966 | 13/16 |
| RA6 / BF＋缓存 | 1.009 | 7/16 |
| RA6-fp64 / Replay-fp64 | 0.972 | 13/16 |
| RA6-fp64 / BF＋缓存-fp64 | 1.041 | 3/16 |

**这是从保存的结果重建表格，不是重新运行实验。** 它验证数据对齐与统计计算，不验证原始流量处理、训练过程、查询正确性或计时。四条轨迹的四个预算不能当作 16 次独立实验。

## 2. 同时复现指纹缓存的公平对照

```bash
python3 scripts/reproduce_results.py --table all --output reproduced
```

输入包括第 5、6、10、11 轮的已提交 CSV。输出：

- `tcp.md`：TCP-only 的 16 个设置和汇总；
- `fingerprint.md`：第十轮与同格式 Replay 的对照；
- `summary.json`：未四舍五入的统计值与案例数；
- `manifest.json`：实际读取文件的相对路径、字节数、SHA-256，以及复现脚本的 SHA-256。

默认不写文件，只有指定 `--output` 才写入；不会覆盖已有输出，重复运行时换一个输出目录。不会改动 `windows_research/` 中的输入或实验脚本。

第十轮预期完整性为：1146 个案例 → 去掉 70 个探测重放案例 → 1076 个主案例 → 按原来的参照误报 ≥30 规则纳入 748 个、排除 328 个。预期 `RA6-fp64/Replay-fp64` 中位数为 **0.996**。

### 防止“只复现了一部分也报成功”

脚本对每个要求的方法检查完整案例集合。以下情况非零退出，不生成成功报告：

- 数据文件、必需列或某个案例缺失；
- 同一方法的同一案例出现重复行；
- 多出不属于已存档实验的案例；
- 误报数不是非负整数，或存档的结构字节数超过预算。

不存在“只取几个文件的交集”后继续报完整结果的做法。文件哈希用于追溯实际输入，不等于独立第三方验证了原始实验真实性。

测试（标准库即可）：

```bash
python3 -m unittest discover -s scripts -p 'test_reproduce_results.py' -v
```

脚本按自身位置定位仓库，不要求从特定工作目录运行；也支持 `--root /path/to/ra-gama` 指定另一份存档。

## 3. 真正执行缓存代码的最小检查

如果已有主 conda 环境，可以运行冻结的缓存测试，不需要任何原始数据：

```bash
PYTHON="$PWD/.condaenv/bin/python" bash scripts/smoke_cache.sh
```

也可以把 `PYTHON` 指向另一处已有且含 `numpy`、`numba` 的环境。脚本不会自动安装依赖。

该测试执行以下检查：

- 指纹宽度和匹配长度都为 40 时，与原缓存各项计数一致；
- 打包数组的物理字节不超预算；
- 一组固定种子的随机输入中，最终缓存没有命中所检查的成员。

第三项是有限输入、最终状态的测试，**不是指纹缓存严格零假阴性的证明**。这也不是训练、筛选、部署全链路的性能复现。

## 4. 从头执行的小规模端到端检查（无原始数据依赖）

已有主 Python 环境时，可以一条命令运行完整的小流程，不需要下载数据或预训练模型：

```bash
.condaenv/bin/python windows_research/round12_nomodel/src/minimal_e2e.py --output reproduced/e2e.json
```

它生成 20,000 行固定种子的合成数据，训练 200 棵树，运行冻结 RA6、共享 Gama 和 BF＋缓存，再使用真实模型数组、BF 位图、CLOCK 缓存执行 150,000 次评估查询。验证原生查询与回放一致、成员检查通过和结构不超预算。

这是 **带成员索引路径的正确性冒烟检查**，不是论文性能证据，不用于声称 RA6 在合成数据上优于 BF＋缓存。当前固定例子中后者反而更好，结果原样保留。首次运行含 Numba 编译，不能用其时间作稳态速度对比。端到端入口已在没有数据缓存的发布仓库中运行通过。

需要的包是既有主环境中的 NumPy、pandas、SciPy、LightGBM 和 Numba，不会自动安装。输出文件不覆盖写；重复运行时换文件名。更多说明见 `windows_research/round12_nomodel/README.md`。

## 5. 重新运行完整数据集的训练与查询

完整环境见根目录 README 的“环境”，数据来源和放置位置见 `data/README.md`。然后按对应实验目录的 README 运行。这个入口不会自动下载大数据或启动长任务。

| 要重跑的内容 | 入口 | 注意 |
|---|---|---|
| 冻结 RA6 主表 | `windows_research/round6_bucket/src/run6.py` | 需要准备对应数据和分数缓存 |
| 原版 Gama / RA6 从训练到查询 | `windows_research/round7_original_e2e/`、`round8_paper_data/` | 两个 Python 环境，串行计时；不能用选择耗时代替完整构建耗时 |
| 指纹缓存与同格式网格 | `windows_research/round10_fpcache/README.md` | 主方法和网格必须使用同一缓存格式 |
| TCP-only 与无模型对照 | `windows_research/round11_tcp/README.md` | 查询为测试负例子流；真实轨迹，不是独立种子的多次实验 |

这里的最小入口不声称复现了每个依赖、每个平台的完整实验。完整环境锁文件主要针对 macOS ARM64；上面的标准库表格复现不依赖该平台。

## 结果解读与共享边界

- “Gama”在第 5/6/10/11 轮对照中是共享实现；作者原版程序的结果在第 7/8 轮，不能混为一组。
- 选择阶段的加速不代表从模型训练到部署的完整构建也更快。
- 同格式 Replay 是指纹版选择器的公平参照；带索引缓存与指纹缓存的比值包含条目大小和可用槽位的差异。
- 默认输出只引用相对路径，但**这不是匿名化工具**：原仓库 URL、提交历史、原始日志与来源名称仍可能暴露身份。不要把此仓库直接当成双盲匿名包。
