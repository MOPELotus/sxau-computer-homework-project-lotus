from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from scipy import sparse
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


NUMERIC_FEATURES = [
    "cases",
    "deaths",
    "culling",
    "neighboring_outbreaks_14d",
    "livestock_density_index",
    "trade_flow_index",
    "transport_access_index",
    "border_distance_km",
    "rainfall_anomaly",
    "temperature_anomaly",
    "case_fatality_rate",
    "outbreak_pressure",
    "border_proximity_score",
    "llm_border_relevance",
    "llm_transmission_complexity",
    "llm_control_pressure",
    "intel_risk_score",
]

CATEGORICAL_FEATURES = [
    "source_platform",
    "country",
    "border_region",
    "disease",
    "host_species",
]

TEXT_FEATURE = "model_text"


@dataclass
class FeaturePack:
    full_features: Any
    feature_names: list[str]
    mode: str


def build_model_text(dataset: pd.DataFrame) -> pd.Series:
    return (
        dataset["narrative_text"].fillna("")
        + " "
        + dataset["llm_summary"].fillna("")
        + " "
        + dataset["llm_key_signals"].fillna("")
        + " "
        + dataset["llm_recommended_action"].fillna("")
    ).str.strip()


class FusionFeatureBuilder:
    def build(self, dataset: pd.DataFrame) -> FeaturePack:
        prepared = dataset.copy()
        prepared[TEXT_FEATURE] = build_model_text(prepared)

        tabular_transformer = ColumnTransformer(
            transformers=[
                (
                    "numeric",
                    Pipeline([("scaler", StandardScaler())]),
                    NUMERIC_FEATURES,
                ),
                (
                    "categorical",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=True),
                    CATEGORICAL_FEATURES,
                ),
            ],
            remainder="drop",
            sparse_threshold=0.3,
        )
        vectorizer = TfidfVectorizer(max_features=120, ngram_range=(1, 2), min_df=1)

        tabular_features = tabular_transformer.fit_transform(prepared)
        text_features = vectorizer.fit_transform(prepared[TEXT_FEATURE])
        full_features = sparse.hstack([sparse.csr_matrix(tabular_features), text_features]).tocsr()

        tabular_names = tabular_transformer.get_feature_names_out().tolist()
        text_names = [f"text__{name}" for name in vectorizer.get_feature_names_out()]
        return FeaturePack(
            full_features=full_features,
            feature_names=tabular_names + text_names,
            mode="结构化特征 + TF-IDF 文本特征",
        )
