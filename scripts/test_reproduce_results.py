"""Standard-library checks; no raw data, submodules, Numba or training required.

Run: python3 -m unittest discover -s scripts -p 'test_reproduce_results.py' -v
"""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import reproduce_results as R


class LoaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'rows').mkdir()
        self.path = self.root / 'rows/rows_example.csv'
        self.row = dict(dataset='example', budget_kib='1', workload='once', seed='0',
                        method='BF', fp_tail='7', total_bytes='1024')
        self.expected = {('example', 1, 'once', 0)}

    def write(self, rows):
        with self.path.open('w', encoding='utf-8', newline='') as fh:
            writer = csv.DictWriter(fh, fieldnames=list(self.row))
            writer.writeheader()
            writer.writerows(rows)

    def load(self):
        return R.Archive(self.root).rows('rows', ('BF',), self.expected)

    def test_load_count_and_digest(self):
        self.write([self.row])
        archive = R.Archive(self.root)
        rows = archive.rows('rows', ('BF',), self.expected)
        self.assertEqual(rows['example', 1, 'once', 0]['BF']['fp_tail'], 7)
        self.assertEqual(archive.files['rows/rows_example.csv']['sha256'],
                         hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_missing_file_fails(self):
        with self.assertRaisesRegex(R.DataError, 'No result CSVs'):
            self.load()

    def test_missing_case_fails(self):
        self.write([])
        with self.assertRaisesRegex(R.DataError, 'missing'):
            self.load()

    def test_duplicate_case_fails(self):
        self.write([self.row, self.row])
        with self.assertRaisesRegex(R.DataError, 'duplicate'):
            self.load()

    def test_unexpected_case_fails(self):
        self.write([dict(self.row, seed='1')])
        with self.assertRaisesRegex(R.DataError, 'unexpected case'):
            self.load()

    def test_bad_count_fails(self):
        for value in ('nan', '-1', '2.5', ''):
            with self.subTest(value=value):
                self.write([dict(self.row, fp_tail=value)])
                with self.assertRaises(R.DataError):
                    self.load()

    def test_over_budget_fails(self):
        self.write([dict(self.row, total_bytes='1025')])
        with self.assertRaisesRegex(R.DataError, 'exceeds budget'):
            self.load()

    def test_truncated_row_fails(self):
        self.write([self.row])
        self.path.write_text(self.path.read_text().rsplit(',', 1)[0] + '\n')
        with self.assertRaisesRegex(R.DataError, 'incomplete CSV row'):
            self.load()

    def test_existing_report_not_overwritten(self):
        dest = self.root / 'output'
        R.write_outputs(dest, {'table.md': 'old'})
        with self.assertRaisesRegex(R.DataError, 'already exists'):
            R.write_outputs(dest, {'summary.json': '{}', 'table.md': 'new'})
        self.assertEqual((dest / 'table.md').read_text(), 'old')
        self.assertFalse((dest / 'summary.json').exists())


class ArchiveRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs, cls.summary = R.reproduce(R.ROOT, 'all')

    def test_tcp_regression(self):
        s = self.summary['tcp']
        self.assertEqual(s['cases'], 16)
        expected = {'RA6/Gama': (.416, 16), 'RA6/Replay': (.966, 13),
                    'RA6/BF+cache': (1.009, 7), 'RA6-fp64/Replay-fp64': (.972, 13),
                    'RA6-fp64/BF+cache-fp64': (1.041, 3)}
        for name, (med, wins) in expected.items():
            self.assertEqual(round(s['comparisons'][name]['median'], 3), med)
            self.assertEqual(s['comparisons'][name]['not_worse'], wins)
        # Correct the archived prose's old minimum (0.991); MAWI-20/64 is 0.980.
        self.assertEqual(round(s['comparisons']['RA6-fp64/BF+cache-fp64']['minimum'], 3), .980)

    def test_fingerprint_regression(self):
        s = self.summary['fingerprint']
        for k, v in dict(cases=1146, main_cases=1076, included=748, excluded=328,
                         no_repeat_cases=140, no_repeat_equal_fp=140, final_cache_member_hits=0).items():
            self.assertEqual(s[k], v)
        for name, med in {'RA6-fp64/RA6': 1.050, 'RA6-fp64/Gama': .097,
                          'RA6-fp64/Replay-fp64': .996, 'RA6/Replay': .999,
                          'Replay-fp64/Replay': 1.049}.items():
            self.assertEqual(round(s['comparisons'][name]['median'], 3), med)

    def test_deterministic_relative_manifest(self):
        again, _ = R.reproduce(R.ROOT, 'all')
        self.assertEqual(self.outputs, again)
        manifest = json.loads(self.outputs['manifest.json'])
        self.assertEqual(manifest['mode'], 'archived-results-only')
        self.assertGreater(len(manifest['inputs']), 0)
        for relative, record in manifest['inputs'].items():
            self.assertFalse(Path(relative).is_absolute())
            self.assertEqual(hashlib.sha256((R.ROOT / relative).read_bytes()).hexdigest(), record['sha256'])

    def test_cli_from_another_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, '-I', str(R.ROOT / 'scripts/reproduce_results.py'),
                                     '--table', 'tcp', '--output', str(Path(tmp) / 'out')],
                                    cwd=tmp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            saved = json.loads((Path(tmp) / 'out/summary.json').read_text())
            self.assertEqual(saved['tcp'], self.summary['tcp'])

    def test_cli_failure_has_no_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'out'
            result = subprocess.run([sys.executable, str(R.ROOT / 'scripts/reproduce_results.py'),
                                     '--root', tmp, '--output', str(out)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('复现失败', result.stderr)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
