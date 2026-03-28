from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from disease_intel.pipeline import run_pipeline


class PipelineSmokeTest(unittest.TestCase):
    def test_folder_pipeline_runs_in_heuristic_mode(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        input_path = project_root / "materials" / "source"

        with tempfile.TemporaryDirectory() as temp_dir:
            summary = run_pipeline(
                source_path=input_path,
                output_dir=temp_dir,
                llm_mode="heuristic",
            )

            self.assertEqual(summary["llm_mode"], "heuristic")
            self.assertEqual(summary["model_mode"], "supervised")

            metrics_path = Path(temp_dir) / "metrics.json"
            predictions_path = Path(temp_dir) / "predictions.csv"
            standardized_path = Path(temp_dir) / "standardized_dataset.csv"
            ingest_report_path = Path(temp_dir) / "ingest_report.json"

            self.assertTrue(metrics_path.exists())
            self.assertTrue(predictions_path.exists())
            self.assertTrue(standardized_path.exists())
            self.assertTrue(ingest_report_path.exists())

            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            ingest_report = json.loads(ingest_report_path.read_text(encoding="utf-8"))
            self.assertIn("f1", metrics)
            self.assertGreaterEqual(ingest_report["record_count"], 9)


if __name__ == "__main__":
    unittest.main()
