from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from disease_intel.pipeline import run_pipeline


class PipelineSmokeTest(unittest.TestCase):
    def test_demo_pipeline_runs_in_heuristic_mode(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        input_path = project_root / "data" / "sample" / "outbreak_events_sample.csv"

        with tempfile.TemporaryDirectory() as temp_dir:
            summary = run_pipeline(
                input_path=input_path,
                output_dir=temp_dir,
                llm_mode="heuristic",
                use_embeddings=False,
            )

            self.assertEqual(summary["llm_mode"], "heuristic")
            self.assertEqual(summary["feature_mode"], "tfidf")

            metrics_path = Path(temp_dir) / "metrics.json"
            predictions_path = Path(temp_dir) / "predictions.csv"
            self.assertTrue(metrics_path.exists())
            self.assertTrue(predictions_path.exists())

            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            self.assertIn("f1", metrics)
            self.assertIn("roc_auc", metrics)


if __name__ == "__main__":
    unittest.main()
