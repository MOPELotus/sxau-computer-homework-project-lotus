from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

from .features import FeaturePack


@dataclass
class TrainingArtifacts:
    estimator: LogisticRegression | None
    mode: str
    metrics: dict[str, float | None | str]
    test_predictions: pd.DataFrame
    full_predictions: pd.DataFrame
    feature_importance: pd.DataFrame


class DiseaseRiskModel:
    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state

    def fit(self, feature_pack: FeaturePack, dataset: pd.DataFrame) -> TrainingArtifacts:
        labels = dataset["cross_border_alert"].to_numpy()
        label_available = dataset["label_available"].to_numpy().astype(bool)
        labeled_indices = np.where(label_available)[0]

        if len(labeled_indices) >= 6 and len(np.unique(labels[labeled_indices])) >= 2:
            return self._fit_supervised(feature_pack, dataset, labeled_indices)

        return self._fit_score_only(dataset)

    def _fit_supervised(
        self,
        feature_pack: FeaturePack,
        dataset: pd.DataFrame,
        labeled_indices: np.ndarray,
    ) -> TrainingArtifacts:
        labels = dataset["cross_border_alert"].to_numpy()
        train_indices, test_indices = train_test_split(
            labeled_indices,
            test_size=0.25,
            random_state=self.random_state,
            stratify=labels[labeled_indices],
        )

        estimator = LogisticRegression(
            max_iter=2000,
            random_state=self.random_state,
            class_weight="balanced",
            solver="liblinear",
        )
        estimator.fit(feature_pack.full_features[train_indices], labels[train_indices])

        test_probability = estimator.predict_proba(feature_pack.full_features[test_indices])[:, 1]
        test_prediction = (test_probability >= 0.5).astype(int)
        full_probability = estimator.predict_proba(feature_pack.full_features)[:, 1]

        metrics = {
            "mode": "supervised",
            "accuracy": round(float(accuracy_score(labels[test_indices], test_prediction)), 4),
            "precision": round(float(precision_score(labels[test_indices], test_prediction, zero_division=0)), 4),
            "recall": round(float(recall_score(labels[test_indices], test_prediction, zero_division=0)), 4),
            "f1": round(float(f1_score(labels[test_indices], test_prediction, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(labels[test_indices], test_probability)), 4),
        }

        full_predictions = dataset.copy()
        full_predictions["risk_probability"] = np.round(full_probability, 4)
        full_predictions["risk_level"] = np.where(
            full_predictions["risk_probability"] >= 0.7,
            "高风险",
            np.where(full_predictions["risk_probability"] >= 0.4, "中风险", "低风险"),
        )

        test_predictions = full_predictions.iloc[test_indices].copy()
        test_predictions["predicted_alert"] = test_prediction

        coefficients = np.abs(estimator.coef_[0])
        feature_importance = pd.DataFrame(
            {
                "feature": feature_pack.feature_names,
                "importance": coefficients,
            }
        ).sort_values("importance", ascending=False)

        return TrainingArtifacts(
            estimator=estimator,
            mode="supervised",
            metrics=metrics,
            test_predictions=test_predictions,
            full_predictions=full_predictions,
            feature_importance=feature_importance,
        )

    def _fit_score_only(self, dataset: pd.DataFrame) -> TrainingArtifacts:
        score = (
            0.32 * dataset["intel_risk_score"]
            + 0.18 * dataset["border_proximity_score"]
            + 0.16 * np.clip(dataset["trade_flow_index"] / 100, 0, 1)
            + 0.14 * np.clip(dataset["transport_access_index"] / 100, 0, 1)
            + 0.10 * np.clip(dataset["neighboring_outbreaks_14d"] / 10, 0, 1)
            + 0.10 * np.clip(dataset["outbreak_pressure"] / 8, 0, 1)
        ).clip(0, 1)

        full_predictions = dataset.copy()
        full_predictions["risk_probability"] = np.round(score, 4)
        full_predictions["risk_level"] = np.where(
            full_predictions["risk_probability"] >= 0.7,
            "高风险",
            np.where(full_predictions["risk_probability"] >= 0.4, "中风险", "低风险"),
        )

        feature_importance = pd.DataFrame(
            {
                "feature": [
                    "intel_risk_score",
                    "border_proximity_score",
                    "trade_flow_index",
                    "transport_access_index",
                    "neighboring_outbreaks_14d",
                    "outbreak_pressure",
                ],
                "importance": [0.32, 0.18, 0.16, 0.14, 0.10, 0.10],
            }
        )

        return TrainingArtifacts(
            estimator=None,
            mode="score_only",
            metrics={
                "mode": "score_only",
                "accuracy": None,
                "precision": None,
                "recall": None,
                "f1": None,
                "roc_auc": None,
            },
            test_predictions=full_predictions.iloc[0:0].copy(),
            full_predictions=full_predictions,
            feature_importance=feature_importance,
        )
