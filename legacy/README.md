# legacy：LightTree-PLBF 学生 vs Gama 教师（早期研究，存档）

这些脚本是在 RA-PLBF 之前做的另一条线：用轻量树模型做学生、Gama 的 LBF 做教师，记录在 `做了什么..md`、`实验结果.md`、`老师的思路.md`。只作存档，不参与后面任何一轮的结果。

- 脚本按自身所在目录找 `LBF-Gama/`：把作者的 Gama 仓库检出（或软链接）到 `legacy/LBF-Gama/`，数据放在其 `dataset/` 下。
- 需要 scikit-learn，主环境里没有，可以用 `.condaenv_gama`。
- 整理仓库时只修了 `evaluate_url_cod.py` 第 53 行一个误输入的 `“` 字符（原文件因此无法解析），其他代码未改动。
