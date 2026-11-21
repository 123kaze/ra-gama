# Research notes / 研究文档

- [思考.md](思考.md)：用户提供的耦合优化研究想法，原文同步；其中理论与文献判断不等于已完成的实验或已验证定理。
- [轻量模型与缓存感知Bloom过滤器：研究思路](轻量模型与缓存感知Bloom过滤器_研究思路.md)：讨论目标、场景、候选模型和分阶段验证安排。

本次同步来自公开实验仓库 `123kaze/CPP_Learing_CS106X` 的 `bloom/submission-baselines` 分支、提交 `9336221448d01b2ed743bcea9d74133301a47479`，只复制明确选定的文档和实验文件，不合并其Git历史。

第21轮共享回放两版仅为已停止／已取消的部分归档，不是完整性能结果；第23–26轮为已完成的小规模探索。它们不是对冻结RA6或论文主实验的无声替换。

Some experiment notes preserve the branch/publication state at the time of the original run. These records are now mirrored here; no cancelled job was restarted and no previously removed experiment was restored by this sync.

## 2026-11-22：第27–31轮与执行计划

- [实验与审查修复计划（完成后勾选）](实验与审查修复计划_20261121.md)
- [稿件表述建议与历史待审阅补丁](review_claims_20261121/README.md)：不是完整更新或新编译的论文；最新指示是不再改稿、不恢复已产生的局部改动，只继续实验和MD。
- [标准库只读核验器](verify_rounds27_31.py)
- [已核验的发布提交与范围](publication_rounds27_31.json)：计划表发布勾选为推送成功后补记，不是预先宣称成功。
- [真实HTTP结果](../windows_research/round27_http_real/README.md)
- [重加权机制与散点图](../windows_research/round28_reweight_mechanism/README.md)
- [聚类区间与资源明细](../windows_research/round29_evidence_audit_v2/README.md)
- [审查数值核验](../windows_research/round30_submission_audit/README.md)
- [SQL确认后才插入负缓存的312条计时](../windows_research/round31_sqlite_online/README.md)

这批实验文件精确同步自CPP实验分支提交`d9c2fe31dd0ac7e9a1a6eac3a41bb72eebc05f3e`，不合并实验仓库Git历史。Round29v1保留为失败归档；两次NASA下载超时也保留日志。原始日志、预处理缓存、临时SQLite数据库和无关工作文件不发布。第29轮依赖的report17历史文字差异有精确hash兼容记录，不恢复用户删除的表述。

## 第32–34轮：后续授权同步

用户在CPP-only推送完成后，明确要求“ragama也提交一下”。本次因此同步CPP提交`a1238f7ada8cc4ec1e7c4b546799f87120a16d8f`中的第32–34轮及相关MD，不改变之前CPP-only回执的历史含义；计划表中当时的指令记录保留。

- [NR32的140逐字节回归](../windows_research/round32_no_repeat_guard/README.md)
- [GT归一化180记录](../windows_research/round33_gt_normalization_v2/README.md)
- [第33轮v1停止归档](../windows_research/round33_gt_normalization/STATUS.md)
- [人工后端成本288计时](../windows_research/round34_backend_cost/README.md)
- [32–34轮只读核验器](verify_rounds32_34.py)
- [此前CPP-only发布回执](publication_rounds32_34_cpp_only.json)

同步不含论文仓库、原始数据或临时数据库，不强推，不恢复已删除实验，不移动`pvldb-submission`标签。
