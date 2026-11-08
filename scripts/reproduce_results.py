#!/usr/bin/env python3
"""Recompute selected tables from committed CSVs using only Python's standard library.

This checks archived results, not a rerun of training, queries or timing. Frozen
experiment code, datasets, conda environments and submodules are not required.
"""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from statistics import median
import sys

ROOT = Path(__file__).resolve().parents[1]
TCP_BUDGETS = {
    'caida_tcp_flow': (16, 32, 63, 189),
    'mawi2020_tcp_flow': (32, 64, 127, 381),
    'mawi2021_tcp_flow': (21, 41, 81, 242),
    'mawi2022_tcp_flow': (32, 64, 128, 382),
}
MAIN_BUDGETS = {
    'caida': (128, 256, 1024, 2048), 'cod': (256, 1024, 4096),
    'shalla': (256, 1024, 2048, 4096), 'url': (64, 128, 256),
    'caida_flow': (16, 24, 32, 256), 'mawi2020_flow': (16, 24, 32, 128),
    'mawi2021_flow': (16, 24, 32, 128), 'mawi2022_flow': (16, 24, 32, 128),
}
PROBE = '探测重放10%'
NOREPEAT = ('每key一次', '全新对抗')
MIN_REF = 30


class DataError(ValueError):
    """A missing, duplicate or malformed archived result."""


def require(condition, message):
    if not condition:
        raise DataError(message)


def integer(value, context):
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise DataError(f'{context}: expected a non-negative integer, got {value!r}') from exc
    require(result >= 0, f'{context}: negative count')
    return result


def ratio(a, b):
    return (a + 1) / (b + 1)


def stats(values):
    values = list(values)
    require(bool(values), 'No cases to summarize')
    return dict(cases=len(values), median=median(values), minimum=min(values),
                maximum=max(values), not_worse=sum(v <= 1 for v in values))


class Archive:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.files = {}

    def read(self, relative):
        path = self.root / relative
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise DataError(f'Cannot read {relative}: {exc.strerror}') from exc
        self.files[relative] = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        return raw.decode('utf-8')

    def rows(self, folder, methods, expected):
        """Validate each requested method over the entire expected case set.

        Do not silently intersect incomplete result sets. Irrelevant sensitivity
        methods are ignored; duplicate rows for a requested method are errors.
        """
        paths = sorted((self.root / folder).glob('rows_*.csv'))
        require(bool(paths), f'No result CSVs in {folder}')
        result = {}
        required = {'dataset', 'budget_kib', 'workload', 'seed', 'method', 'fp_tail'}
        for path in paths:
            rel = path.relative_to(self.root).as_posix()
            reader = csv.DictReader(io.StringIO(self.read(rel)))
            require(required <= set(reader.fieldnames or []), f'{rel}: missing CSV columns')
            for line, row in enumerate(reader, 2):
                if row['method'] not in methods:
                    continue
                where = f'{rel}:{line}'
                require(None not in row and all(v is not None for v in row.values()),
                        f'{where}: incomplete CSV row')
                key = (row['dataset'], integer(row['budget_kib'], where),
                       row['workload'], integer(row['seed'], where))
                require(key in expected, f'{where}: unexpected case {key}')
                method = row['method']
                require(method not in result.setdefault(key, {}),
                        f'{where}: duplicate {method} for {key}')
                row['fp_tail'] = integer(row['fp_tail'], where)
                if 'total_bytes' in row:
                    used = integer(row['total_bytes'], where)
                    require(used <= key[1] * 1024, f'{where}: saved structure exceeds budget')
                result[key][method] = row
        for key in sorted(expected):
            missing = set(methods) - result.get(key, {}).keys()
            require(not missing, f'{folder}: missing {sorted(missing)} for {key}')
        return result


def main_cases():
    cases = set()
    for ds, budgets in MAIN_BUDGETS.items():
        if ds.endswith('_flow'):
            workloads, seeds = ['真实轨迹'], [0]
        else:
            pools = ['1万', '10万'] + (['100万'] if ds == 'caida' else []) + ['全部']
            workloads = [f'{dist}-{pool}' for pool in pools
                         for dist in ('uniform', 'zipf0.8', 'zipf1.0', 'zipf1.2')]
            workloads += list(NOREPEAT) + [PROBE]
            seeds = range(5)
        cases.update((ds, kib, w, seed) for kib in budgets for w in workloads for seed in seeds)
    return cases


def tcp_table(archive):
    expected = {(ds, kib, '真实轨迹', 0) for ds, budgets in TCP_BUDGETS.items() for kib in budgets}
    root = 'windows_research/round11_tcp/results/'
    data = {}
    for folder, methods in (
        ('run5/results', ('Gama', 'Gama+10%', 'LearnGrid')),
        ('run6/results/main', ('RA6',)),
        ('run10/results/main', ('RA6-fp64',)),
        ('grid10/results/grid', ('LearnGrid-fp64',)),
        ('nomodel', ('BF', 'BF+缓存', 'BF-fp64', 'BF+缓存-fp64')),
    ):
        for key, rows in archive.rows(root + folder, methods, expected).items():
            data.setdefault(key, {}).update(rows)
    pairs = {
        'RA6/Gama': ('RA6', 'Gama'),
        'RA6/Replay': ('RA6', 'LearnGrid'),
        'RA6/BF+cache': ('RA6', 'BF+缓存'),
        'RA6-fp64/Replay-fp64': ('RA6-fp64', 'LearnGrid-fp64'),
        'RA6-fp64/BF+cache-fp64': ('RA6-fp64', 'BF+缓存-fp64'),
    }
    summary = {name: stats(ratio(r[a]['fp_tail'], r[b]['fp_tail']) for r in data.values())
               for name, (a, b) in pairs.items()}
    lines = ['# TCP-only：复现第十一轮已保存的 16 个设置', '',
             '这不是新实验。所有数字来自已提交 CSV；只统计原协议的评估段。',
             '这是第十一轮的保守 BF 头开销对照。最新实际开销强基线见 round12_nomodel/results/结论.md，不混用两轮数字。',
             '每条轨迹只有一个查询序列，4 个预算不是 4 次独立重复。', '',
             '| 数据集 | KiB | BF | BF+缓存 | Gama | Replay | RA6 | RA6-fp64 | Replay-fp64 | BF+缓存-fp64 |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    columns = ('BF', 'BF+缓存', 'Gama', 'LearnGrid', 'RA6', 'RA6-fp64', 'LearnGrid-fp64', 'BF+缓存-fp64')
    for ds, budgets in TCP_BUDGETS.items():
        for kib in budgets:
            r = data[ds, kib, '真实轨迹', 0]
            require(r['BF']['fp_tail'] == r['BF-fp64']['fp_tail'],
                    f'{ds}/{kib}: cache-free BF counts differ between cache variants')
            cells = [ds, str(kib)] + [f"{r[m]['fp_tail']:,}" for m in columns]
            lines.append('| ' + ' | '.join(cells) + ' |')
    lines += ['', '比值逐案例使用 `(FP_a + 1)/(FP_b + 1)`，再取中位数；没有显著性检验。', '']
    lines += summary_table(summary)
    lines += ['', 'Gama 是共享实现，不是作者原版程序。指纹缓存只与同格式 Replay/BF+缓存比较。',
              'BF+缓存的比例由学习期回放选择；该对照不能单独证明模型完全没有作用。']
    return '\n'.join(lines) + '\n', dict(cases=len(expected), comparisons=summary)


def summary_table(summary):
    lines = ['| 比较 | 案例 | 中位 | 最小 | 最大 | 不差于参照 |',
             '|---|---:|---:|---:|---:|---:|']
    for name, s in summary.items():
        lines.append(f"| {name} | {s['cases']} | {s['median']:.3f} | {s['minimum']:.3f} | "
                     f"{s['maximum']:.3f} | {s['not_worse']}/{s['cases']} |")
    return lines


def fingerprint_table(archive):
    expected = main_cases()
    root = 'windows_research/'
    r5 = archive.rows(root + 'round5_dp/results', ('RA4', 'Gama', 'LearnGrid'), expected)
    r6 = archive.rows(root + 'round6_bucket/results/main', ('RA6',), expected)
    r10 = archive.rows(root + 'round10_fpcache/results/main', ('RA6-fp64',), expected)
    grid = archive.rows(root + 'round10_fpcache/results/grid', ('LearnGrid-fp64',), expected)
    main = sorted(k for k in expected if k[2] != PROBE)
    included = []
    for k in main:
        raw = r5[k]['RA4'].get('fp_oracle')
        require(raw is not None, f'Missing reference for {k}')
        try:
            ref = float(raw) if raw != '' else r5[k]['LearnGrid']['fp_tail']
        except ValueError as exc:
            raise DataError(f'Invalid reference for {k}: {raw!r}') from exc
        require(math.isfinite(ref) and ref >= 0 and ref == int(ref), f'Invalid reference for {k}')
        if ref >= MIN_REF:
            included.append(k)
    summary = {}
    for name, left, lm, right, rm in (
        ('RA6-fp64/RA6', r10, 'RA6-fp64', r6, 'RA6'),
        ('RA6-fp64/Gama', r10, 'RA6-fp64', r5, 'Gama'),
        ('RA6-fp64/Replay-fp64', r10, 'RA6-fp64', grid, 'LearnGrid-fp64'),
        ('RA6/Replay', r6, 'RA6', r5, 'LearnGrid'),
        ('Replay-fp64/Replay', grid, 'LearnGrid-fp64', r5, 'LearnGrid'),
    ):
        summary[name] = stats(ratio(left[k][lm]['fp_tail'], right[k][rm]['fp_tail']) for k in included)
    norep = [k for k in main if k[2] in NOREPEAT]
    equal = sum(r10[k]['RA6-fp64']['fp_tail'] == r5[k]['Gama']['fp_tail'] for k in norep)
    member_hits = sum(integer(r10[k]['RA6-fp64']['member_hits_final'], str(k)) for k in expected)
    lines = ['# 指纹缓存：同格式网格对照的存档复现', '',
             f'完整性：{len(expected)} 个案例；去除探测重放后 {len(main)} 个；',
             f'按存档规则（原 Hindsight，否则原 Replay，误报 ≥{MIN_REF}）纳入 {len(included)} 个，'
             f'排除 {len(main) - len(included)} 个。没有只取各目录交集来掩盖缺失结果。', '']
    lines += summary_table(summary)
    lines += ['', f'无重复负载：指纹版与 Gama 的误报计数相同 {equal}/{len(norep)}；仅比较计数，不据此声称结构逐位相同。',
              f'存档记录的最终缓存成员误命中数合计：{member_hits}。此检查不覆盖整个运行过程的所有缓存状态，',
              '也不是指纹缓存严格零假阴性的保证；发生碰撞仍可能拒绝成员。', '',
              '以上是中位数，不是平均值。缓存格式间的比值不是纯选择算法收益；',
              '公平的选择器对比是 RA6/Replay 和 RA6-fp64/Replay-fp64。']
    return '\n'.join(lines) + '\n', dict(cases=len(expected), main_cases=len(main),
        included=len(included), excluded=len(main) - len(included),
        no_repeat_cases=len(norep), no_repeat_equal_fp=equal,
        final_cache_member_hits=member_hits, comparisons=summary)


def reproduce(root, table='tcp'):
    archive = Archive(root)
    outputs, summaries = {}, {}
    builders = {'tcp': tcp_table, 'fingerprint': fingerprint_table}
    selected = builders if table == 'all' else (table,)
    for name in selected:
        outputs[name + '.md'], summaries[name] = builders[name](archive)
    manifest = dict(schema_version=1, mode='archived-results-only',
                    inputs=dict(sorted(archive.files.items())))
    manifest['runner_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for name, data in (('summary.json', summaries), ('manifest.json', manifest)):
        outputs[name] = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    return outputs, summaries


def write_outputs(folder, outputs):
    """Do not overwrite a previous report or any original result files."""
    folder = Path(folder)
    for name in outputs:
        require(not (folder / name).exists(), f'Output already exists: {folder / name}; choose a new directory')
    folder.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        with (folder / name).open('x', encoding='utf-8') as fh:
            fh.write(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='Research repository root (default: this checkout)')
    parser.add_argument('--table', choices=('tcp', 'fingerprint', 'all'), default='tcp')
    parser.add_argument('--output', type=Path, help='New output directory; default prints Markdown without writing files')
    args = parser.parse_args()
    try:
        outputs, _ = reproduce(args.root, args.table)
        if args.output:
            write_outputs(args.output, outputs)
            print(f'已复现存档结果 → {args.output}；未训练模型、未重新回放或计时。')
        else:
            print('\n'.join(content for name, content in outputs.items() if name.endswith('.md')), end='')
    except (DataError, OSError, UnicodeError) as exc:
        parser.exit(1, f'复现失败：{exc}\n')


if __name__ == '__main__':
    main()
