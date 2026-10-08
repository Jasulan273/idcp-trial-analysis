import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from idcp_trial.analysis import COLUMNS, Pair, read_pairs, summarize, svg_chart

ROOT = Path(__file__).resolve().parents[1]
class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / "pairs.csv"

    def write(self, row):
        self.file.write_text(",".join(COLUMNS) + "\n" + row + "\n", encoding="utf-8")

    def test_sample_known_medians_and_failed_tasks(self):
        source = ROOT / "data/example_pairs.csv"
        result = summarize(read_pairs(source), source)
        self.assertEqual(result["pair_count"], 8)
        self.assertEqual(result["baseline_median_minutes"], 27)
        self.assertEqual(result["idcp_with_correction_median_minutes"], 23)
        self.assertAlmostEqual(result["reduction_of_medians_percent"], 14.814815)
        self.assertEqual(result["failed_count"], 2)
        self.assertEqual(result["evidence_complete_percent"], 87.5)

    def test_corrections_can_turn_savings_negative(self):
        self.write("A,10,8,5,failed,false")
        result = summarize(read_pairs(self.file), self.file)
        self.assertEqual(result["reduction_of_medians_percent"], -30)

    def test_paired_median_is_different_from_reduction_of_medians(self):
        self.write("A,10,5,0,accepted,true\nB,100,90,0,accepted,true")
        result = summarize(read_pairs(self.file), self.file)
        self.assertEqual(result["median_paired_reduction_percent"], 30)
        self.assertNotEqual(result["median_paired_reduction_percent"], result["reduction_of_medians_percent"])

    def test_invalid_inputs_rejected(self):
        for row in ("A,0,8,0,accepted,true", "A,nan,8,0,accepted,true", "A,10,inf,0,accepted,true", "A,10,8,-1,accepted,true", "A,10,8,0,unknown,true", "A,10,8,0,accepted,yes", "A,10,8,0,accepted,true\nA,10,8,0,accepted,true", "A,10,8,0,accepted", "A,10,8,0,accepted,true,extra", ""):
            with self.subTest(row=row):
                self.write(row)
                with self.assertRaises(ValueError):
                    read_pairs(self.file)

    def test_wrong_header_rejected(self):
        self.file.write_text("id,time\nA,10\n")
        with self.assertRaises(ValueError):
            read_pairs(self.file)

    def test_chart_escapes_pair_labels(self):
        chart = svg_chart([Pair("<unsafe>", 10, 8, 0, "accepted", True)])
        self.assertIn("&lt;unsafe&gt;", chart)
        self.assertNotIn("<unsafe>", chart)

    def test_cli_outputs_and_provenance(self):
        out = Path(self.temp.name) / "results"
        command = [sys.executable, "-m", "idcp_trial", str(ROOT / "data/example_pairs.csv"), "--output", str(out)]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads((out / "summary.json").read_text())
        self.assertEqual(len(summary["input_sha256"]), 64)
        self.assertTrue((out / "comparison.svg").exists())

    def test_cli_invalid_input_has_nonzero_exit(self):
        self.write("A,0,8,0,accepted,true")
        result = subprocess.run([sys.executable, "-m", "idcp_trial", str(self.file)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Error:", result.stderr)

if __name__ == "__main__":
    unittest.main()
