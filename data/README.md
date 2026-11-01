# 数据：放在哪里、从哪里来

原始数据、缓存和训练好的模型都不进 git（体积大，部分数据的许可也不允许转发）。代码按下面的固定路径读取，路径都相对于仓库根目录。各目录里的 `*-source.json` / `*-download.json` 记录了我们实际用的下载地址、字节数和 SHA256，已经提交，可以用来核对。

| 数据集（代码里的名字） | 放置位置 | 来源 |
|---|---|---|
| `cod` | `LBF-Gama/dataset/raw/cod/{train,test}.csv` | Kaggle `hari31416/celestialclassify` v1（CC0），免登录下载：`https://www.kaggle.com/api/v1/datasets/download/hari31416/celestialclassify` |
| `caida`、`caida_flow` | `windows_research/data/caida.csv`；`learned_adaptive_hybrid` 读 `learned_adaptive_hybrid/external/How-to-Train-Your-Filter/data/raw/caida.csv` | How-to-Train-Your-Filter 子模块（`c970c34`）的 `data/compressed/caida.tar.gz`，解压即可；`windows_research/src/fetch_data.py` 会下载并校验 |
| `url` | `windows_research/round2_backlog/data/malicious_phish_full.csv` | Kaggle `sid321axn/malicious-urls-dataset` v1（CC0），见 `url-full-source.json` |
| `shalla` | `windows_research/round2_backlog/data/shalla_combined.csv`；`learned_adaptive_hybrid` 读子模块的 `data/raw/shalla_combined.csv` | 子模块的 `data/compressed/shalla.tar.gz`，见 `shalla-source.json` |
| `mawi2020_flow` | `learned_adaptive_hybrid/external/mawi/mawi2020.csv` 和 `windows_research/data/mawi2020.csv` | MAWI samplepoint-F `202004081400`，命令见 `learned_adaptive_hybrid/README.md` |
| `mawi2021_flow` | `learned_adaptive_hybrid/external/mawi/mawi2021.csv` 和 `windows_research/data/mawi2021.csv` | MAWI `202104141400`，`windows_research/src/fetch_mawi.py` |
| `mawi2022_flow` | `windows_research/round2_backlog/data/mawi2022.csv` | MAWI `202204131400`，见 `mawi2022-source.json` |
| `mawi2023_flow`（第四轮留出集） | `windows_research/round4_ra_plbf/data/mawi2023.csv` | MAWI `202304121400`，见该目录的 json |
| `mawi2024_flow`（第六轮留出集） | `windows_research/round6_bucket/data/mawi2024.csv` | MAWI `202404101400`，`windows_research/round6_bucket/src/fetch_holdout2024.py` |

- MAWI 只取每条轨迹开头的一段（`curl -r` 字节区间），用 `tcpdump` 转成文本后再由 `prepare_mawi.py` 解析。MAWI 服务器在头几 MB 之后会严重限速。
- 第一次运行时，各脚本会把数据集转成 `cache/<数据集>/data.npz`，再训练 200 树 LightGBM，结果缓存到 `cache/` 下（`learned_adaptive_hybrid/cache/`、`windows_research/cache/`、`windows_research/round2_backlog/cache/`）。这些都可以删掉重建。
- 原版基线的输入由 `original_baselines/gama/export_csv.py` 等脚本从同一份划分导出到 `original_baselines/*/data/`。
- 第八轮（`windows_research/round8_paper_data/`）按 Gama 论文的原始来源重建 URL 和 COD，生成的数据放在该目录的 `data/`、`inputs/` 下，审计结果见 `results/data_availability.md`。论文作者处理后的 CSV 和划分没有公开，Yelp 的处理后数据和 embedding 也没有公开，所以没有 Yelp。
