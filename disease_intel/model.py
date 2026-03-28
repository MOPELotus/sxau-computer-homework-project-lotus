from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

from .features import FeaturePack


@dataclass
class TrainingArtifacts:
    estimator: LogisticRegression
    metrics: dict[str, float]
    test_predictions: pd.DataFrame
    full_predictions: pd.DataFrame
    feature_importance: pd.DataFrame


class DiseaseRiskModel:
    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state

    def fit(self, feature_pack: FeaturePack, dataset: pd.DataFrame) -> TrainingArtifacts:
        estimator = LogisticRegression(
            max_iter=2000,
            random_state=self.random_state,
            class_weight="balanced",
            solver="liblinear",
        )
        estimator.fit(feature_pack.train_features, feature_pack.train_labels)

        test_probability = estimator.predict_proba(feature_pack.test_features)[:, 1]
        test_prediction = (test_probability >= 0.5).astype(int)
        full_probability = estimator.predict_proba(feature_pack.full_features)[:, 1]

        metrics = {
            "accuracy": round(float(accuracy_score(feature_pack.test_labels, test_prediction)), 4),
            "precision": round(float(precision_score(feature_pack.test_labels, test_prediction, zero_division=0)), 4),
            "recall": round(float(recall_score(feature_pack.test_labels, test_prediction, zero_division=0)), 4),
            "f1": round(float(f1_score(feature_pack.test_labels, test_prediction, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(feature_pack.test_labels, test_probability)), 4),
        }

        full_predictions = dataset.copy()
        full_predictions["risk_probability"] = np.round(full_probability, 4)
        full_predictions["risk_level"] = np.where(
            full_predictions["risk_probability"] >= 0.7,
            "High",
            np.where(full_predictions["risk_probability"] >= 0.4, "Medium", "Low"),
        )

        test_predictions = full_predictions.iloc[feature_pack.test_index].copy()
        test_predictions["predicted_alert"] = test_prediction

        coefficients = np.abs(estimator.coef_[0])
        importance = pd.DataFrame(
            {
                "feature": feature_pack.feature_names,
                "importance": coefficients,
            }
        ).sort_values("importance", ascending=False)

        return TrainingArtifacts(
            estimator=estimator,
            metrics=metrics,
            test_predictions=test_predictions,
            full_predictions=full_predictions,
            feature_importance=importance,
        )
