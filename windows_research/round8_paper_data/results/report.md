# Gama 论文公开原始数据源：作者方法与 RA6 重评估

**不是论文精确数值复现。** 作者最终 CSV、划分和 Yelp embedding 不公开；URL 使用公开作者特征，COD 使用论文链接同一原始源。原样方法参数和测量口径见 README。查询秒是本机实际运行实现的时间，不等同论文服务器时间，更不是纯算法速度消融。

## 数据审计

- paper_url：成员 212,662，负例 427,386；论文 223,088 / 428,118；特征 10 维；精确划分未获得。
- paper_cod：成员 3,000,000，负例 3,000,000；论文 2,498,077 / 2,980,291；特征 49 维；精确划分未获得。
- Yelp：作者过滤后的 CSV、负例生成和完整 embedding 未取得，不伪造替代数据。

## 静态全测试负例池：每个 key 查一次，冷缓存

| 数据/预算KiB | 方法 | 成功重复 | FP中位数 | FPR中位数 | 构建秒 | 全池查询秒 |
|---|---|---:|---:|---:|---:|---:|
| paper_cod 64 | G-LBF(original) | 3 | 243,947 | 10.166547% | 8.468 | 4.757 |
| paper_cod 64 | G-PLBF(original) | 3 | 173,589 | 7.234361% | 9.478 | 14.152 |
| paper_cod 64 | RA6 | 3 | 130,699 | 5.446911% | 317.737 | 0.661 |
| paper_cod 128 | G-LBF(original) | 1 | 133,492 | 5.563309% | 13.647 | 4.657 |
| paper_cod 128 | G-PLBF(original) | 1 | 92,661 | 3.861668% | 14.952 | 14.219 |
| paper_cod 128 | RA6 | 1 | 50,809 | 2.117477% | 281.997 | 3.404 |
| paper_url 64 | G-LBF(original) | 3 | 23,981 | 7.011476% | 0.610 | 0.639 |
| paper_url 64 | G-PLBF(original) | 3 | 19,092 | 5.582048% | 2.167 | 8.881 |
| paper_url 64 | RA6 | 3 | 14,468 | 4.230100% | 29.763 | 0.078 |
| paper_url 128 | G-LBF(original) | 3 | 4,063 | 1.187925% | 1.267 | 0.669 |
| paper_url 128 | G-PLBF(original) | 3 | 2,104 | 0.615160% | 4.747 | 9.137 |
| paper_url 128 | RA6 | 3 | 1,637 | 0.478620% | 29.086 | 0.078 |
| paper_url 192 | G-LBF(original) | 3 | 646 | 0.188875% | 1.423 | 0.729 |
| paper_url 192 | G-PLBF(original) | 3 | 338 | 0.098823% | 5.600 | 8.885 |
| paper_url 192 | RA6 | 3 | 304 | 0.088882% | 30.167 | 0.061 |
| paper_url 256 | G-LBF(original) | 3 | 187 | 0.054674% | 1.836 | 0.723 |
| paper_url 256 | G-PLBF(original) | 3 | 101 | 0.029530% | 8.487 | 9.338 |
| paper_url 256 | RA6 | 3 | 71 | 0.020759% | 29.987 | 0.328 |
| paper_url 320 | G-LBF(original) | 3 | 160 | 0.046780% | 2.581 | 0.810 |
| paper_url 320 | G-PLBF(original) | 3 | 129 | 0.037717% | 7.207 | 9.159 |
| paper_url 320 | RA6 | 3 | 21 | 0.006140% | 30.480 | 0.336 |

## 相同学习期与评估尾段（前25%/后75%）

| 数据/预算KiB | 方法 | 负载 | 成功重复 | 尾段FP | 尾段FPR | 查询秒 | ns/query |
|---|---|---|---:|---:|---:|---:|---:|
| paper_cod 64 | G-LBF(original) | once | 3 | 182,754 | 10.155082% | 4.139 | 2,300 |
| paper_cod 64 | G-LBF(original) | zipf | 3 | 731,315 | 9.750867% | 16.508 | 2,201 |
| paper_cod 64 | G-PLBF(original) | once | 3 | 130,168 | 7.233038% | 11.235 | 6,243 |
| paper_cod 64 | G-PLBF(original) | zipf | 3 | 528,882 | 7.051760% | 46.138 | 6,152 |
| paper_cod 64 | RA6 | once | 3 | 97,961 | 5.443394% | 0.641 | 356 |
| paper_cod 64 | RA6 | zipf | 3 | 184,475 | 2.459667% | 3.364 | 449 |
| paper_cod 128 | G-LBF(original) | once | 1 | 99,968 | 5.554917% | 4.126 | 2,293 |
| paper_cod 128 | G-LBF(original) | zipf | 1 | 300,757 | 4.010093% | 16.317 | 2,176 |
| paper_cod 128 | G-PLBF(original) | once | 1 | 69,588 | 3.866793% | 11.366 | 6,316 |
| paper_cod 128 | G-PLBF(original) | zipf | 1 | 213,880 | 2.851733% | 45.501 | 6,067 |
| paper_cod 128 | RA6 | once | 1 | 38,081 | 2.116045% | 2.766 | 1,537 |
| paper_cod 128 | RA6 | zipf | 1 | 55,836 | 0.744480% | 6.405 | 854 |
| paper_url 64 | G-LBF(original) | once | 3 | 17,966 | 7.003770% | 0.543 | 2,118 |
| paper_url 64 | G-LBF(original) | zipf | 3 | 410,383 | 5.471773% | 15.620 | 2,083 |
| paper_url 64 | G-PLBF(original) | once | 3 | 14,328 | 5.585551% | 6.685 | 26,060 |
| paper_url 64 | G-PLBF(original) | zipf | 3 | 332,978 | 4.439707% | 184.320 | 24,576 |
| paper_url 64 | RA6 | once | 3 | 10,827 | 4.220740% | 0.070 | 272 |
| paper_url 64 | RA6 | zipf | 3 | 102,754 | 1.370053% | 2.566 | 342 |
| paper_url 128 | G-LBF(original) | once | 3 | 3,052 | 1.189775% | 0.561 | 2,188 |
| paper_url 128 | G-LBF(original) | zipf | 3 | 163,600 | 2.181333% | 16.090 | 2,145 |
| paper_url 128 | G-PLBF(original) | once | 3 | 1,571 | 0.612430% | 6.928 | 27,008 |
| paper_url 128 | G-PLBF(original) | zipf | 3 | 28,331 | 0.377747% | 189.240 | 25,232 |
| paper_url 128 | RA6 | once | 3 | 1,203 | 0.468971% | 0.066 | 256 |
| paper_url 128 | RA6 | zipf | 3 | 2,902 | 0.038693% | 1.998 | 266 |
| paper_url 192 | G-LBF(original) | once | 3 | 461 | 0.179714% | 0.620 | 2,418 |
| paper_url 192 | G-LBF(original) | zipf | 3 | 7,795 | 0.103933% | 17.429 | 2,324 |
| paper_url 192 | G-PLBF(original) | once | 3 | 235 | 0.091611% | 6.697 | 26,109 |
| paper_url 192 | G-PLBF(original) | zipf | 3 | 11,822 | 0.157627% | 187.975 | 25,063 |
| paper_url 192 | RA6 | once | 3 | 212 | 0.082645% | 0.056 | 218 |
| paper_url 192 | RA6 | zipf | 3 | 268 | 0.003573% | 11.607 | 1,548 |
| paper_url 256 | G-LBF(original) | once | 3 | 123 | 0.047950% | 0.598 | 2,333 |
| paper_url 256 | G-LBF(original) | zipf | 3 | 2,042 | 0.027227% | 17.036 | 2,272 |
| paper_url 256 | G-PLBF(original) | once | 3 | 72 | 0.028068% | 7.122 | 27,764 |
| paper_url 256 | G-PLBF(original) | zipf | 3 | 1,180 | 0.015733% | 192.101 | 25,613 |
| paper_url 256 | RA6 | once | 3 | 48 | 0.018712% | 0.270 | 1,051 |
| paper_url 256 | RA6 | zipf | 3 | 54 | 0.000720% | 15.496 | 2,066 |
| paper_url 320 | G-LBF(original) | once | 3 | 113 | 0.044051% | 0.680 | 2,652 |
| paper_url 320 | G-LBF(original) | zipf | 3 | 1,917 | 0.025560% | 18.965 | 2,529 |
| paper_url 320 | G-PLBF(original) | once | 3 | 88 | 0.034305% | 6.937 | 27,042 |
| paper_url 320 | G-PLBF(original) | zipf | 3 | 1,406 | 0.018747% | 191.077 | 25,477 |
| paper_url 320 | RA6 | once | 3 | 14 | 0.005458% | 0.267 | 1,040 |
| paper_url 320 | RA6 | zipf | 3 | 11 | 0.000147% | 19.738 | 2,632 |

## 预算与正确性

原版模型按 pickle 计大小而非 RSS，PLBF 后端可能超目标，RA6 索引预算外。预算参数相同不能写成等物理/系统内存。

| 数据/预算KiB | 方法 | 原版pickle/BF目标/BF实际payload B | RA6实际过滤器B（once/zipf） | 预算外索引B |
|---|---|---|---|---:|
| paper_cod 64 | G-LBF(original) | 17,909/47,627/47,628 | — | 0 |
| paper_cod 64 | G-PLBF(original) | 17,909/47,627/100,080 | — | 0 |
| paper_cod 64 | RA6 | — | 64,704/64,790 | 24,000,000 |
| paper_cod 128 | G-LBF(original) | 21,459/109,613/109,614 | — | 0 |
| paper_cod 128 | G-PLBF(original) | 32,101/98,971/203,216 | — | 0 |
| paper_cod 128 | RA6 | — | 130,226/130,248 | 24,000,000 |
| paper_url 64 | G-LBF(original) | 8,798/56,738/56,739 | — | 0 |
| paper_url 64 | G-PLBF(original) | 15,745/49,791/102,000 | — | 0 |
| paper_url 64 | RA6 | — | 64,776/64,837 | 1,701,296 |
| paper_url 128 | G-LBF(original) | 15,745/115,327/115,327 | — | 0 |
| paper_url 128 | G-PLBF(original) | 12,272/118,800/237,896 | — | 0 |
| paper_url 128 | RA6 | — | 130,036/130,124 | 1,701,296 |
| paper_url 192 | G-LBF(original) | 12,272/184,336/184,337 | — | 0 |
| paper_url 192 | G-PLBF(original) | 12,272/184,336/367,080 | — | 0 |
| paper_url 192 | RA6 | — | 195,298/195,476 | 1,701,296 |
| paper_url 256 | G-LBF(original) | 12,272/249,872/249,873 | — | 0 |
| paper_url 256 | G-PLBF(original) | 12,272/249,872/497,456 | — | 0 |
| paper_url 256 | RA6 | — | 260,922/260,805 | 1,701,296 |
| paper_url 320 | G-LBF(original) | 19,257/308,423/308,424 | — | 0 |
| paper_url 320 | G-PLBF(original) | 19,257/308,423/613,872 | — | 0 |
| paper_url 320 | RA6 | — | 326,458/326,234 | 1,701,296 |

## 与论文表2的 G-LBF 数字：不直接计算“复现误差”

论文 URL G-LBF：64/128/192（表头196）/256/320KB 对应 5.471/0.974/0.170/0.060/0.039%。由于最终数据、划分、依赖和硬件不一致，上表只能用于条件明确的重评估。论文 G-PLBF 对照是图7的192KB，不是表2。

## 失败/未完成

尚无已记录错误；完整性请看每行成功重复次数，不能把阶段结果当3次完成。
