from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .llm import SiliconFlowClient


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
LABEL_COLUMN = "cross_border_alert"


@dataclass
class FeaturePack:
    train_features: Any
    test_features: Any
    full_features: Any
    train_labels: np.ndarray
    test_labels: np.ndarray
    feature_names: list[str]
    train_index: np.ndarray
    test_index: np.ndarray
    mode: str


def build_model_text(dataset: pd.DataFrame) -> pd.Series:
    return (
        dataset["narrative_text"].fillna("")
        + " "
        + dataset["llm_summary"].fillna("")
        + " "
        + dataset["llm_key_signals"].fillna("")
    ).str.strip()


class FusionFeatureBuilder:
    def __init__(self, client: SiliconFlowClient | None = None) -> None:
        self.client = client

    def build(
        self,
        dataset: pd.DataFrame,
        use_api_embeddings: bool = False,
        random_state: int = 42,
        test_size: float = 0.25,
    ) -> FeaturePack:
        prepared = dataset.copy()
        prepared[TEXT_FEATURE] = build_model_text(prepared)
        labels = prepared[LABEL_COLUMN].to_numpy()
        indices = np.arange(len(prepared))

        train_index, test_index = train_test_split(
            indices,
            test_size=test_size,
            random_state=random_state,
            stratify=labels,
        )

        train_frame = prepared.iloc[train_index].reset_index(drop=True)
        test_frame = prepared.iloc[test_index].reset_index(drop=True)

        if use_api_embeddings and self.client is not None:
            return self._build_embedding_pack(prepared, train_frame, test_frame, train_index, test_index)

        return self._build_tfidf_pack(prepared, train_frame, test_frame, train_index, test_index)

    def _build_tfidf_pack(
        self,
        full_frame: pd.DataFrame,
        train_frame: pd.DataFrame,
        test_frame: pd.DataFrame,
        train_index: np.ndarray,
        test_index: np.ndarray,
    ) -> FeaturePack:
        tabular_transformer = self._build_tabular_transformer(dense_output=False)
        vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2), min_df=1)

        train_tabular = tabular_transformer.fit_transform(train_frame)
        test_tabular = tabular_transformer.transform(test_frame)
        full_tabular = tabular_transformer.transform(full_frame)

        train_text = vectorizer.fit_transform(train_frame[TEXT_FEATURE])
        test_text = vectorizer.transform(test_frame[TEXT_FEATURE])
        full_text = vectorizer.transform(full_frame[TEXT_FEATURE])

        train_features = sparse.hstack([sparse.csr_matrix(train_tabular), train_text]).tocsr()
        test_features = sparse.hstack([sparse.csr_matrix(test_tabular), test_text]).tocsr()
        full_features = sparse.hstack([sparse.csr_matrix(full_tabular), full_text]).tocsr()

        tabular_names = tabular_transformer.get_feature_names_out().tolist()
        text_names = [f"text__{name}" for name in vectorizer.get_feature_names_out()]
        feature_names = tabular_names + text_names

        return FeaturePack(
            train_features=train_features,
            test_features=test_features,
            full_features=full_features,
            train_labels=train_frame[LABEL_COLUMN].to_numpy(),
            test_labels=test_frame[LABEL_COLUMN].to_numpy(),
            feature_names=feature_names,
            train_index=train_index,
            test_index=test_index,
            mode="tfidf",
        )

    def _build_embedding_pack(
        self,
        full_frame: pd.DataFrame,
        train_frame: pd.DataFrame,
        test_frame: pd.DataFrame,
        train_index: np.ndarray,
        test_index: np.ndarray,
    ) -> FeaturePack:
        tabular_transformer = self._build_tabular_transformer(dense_output=True)
        train_tabular = np.asarray(tabular_transformer.fit_transform(train_frame))
        test_tabular = np.asarray(tabular_transformer.transform(test_frame))
        full_tabular = np.asarray(tabular_transformer.transform(full_frame))

        train_embeddings = np.asarray(self.client.embed_texts(train_frame[TEXT_FEATURE].tolist()))
        test_embeddings = np.asarray(self.client.embed_texts(test_frame[TEXT_FEATURE].tolist()))
        full_embeddings = np.asarray(self.client.embed_texts(full_frame[TEXT_FEATURE].tolist()))

        train_features = np.hstack([train_tabular, train_embeddings])
        test_features = np.hstack([test_tabular, test_embeddings])
        full_features = np.hstack([full_tabular, full_embeddings])

        tabular_names = tabular_transformer.get_feature_names_out().tolist()
        embedding_names = [
            f"embedding__{index:04d}"
            for index in range(train_embeddings.shape[1])
        ]

        return FeaturePack(
            train_features=train_features,
            test_features=test_features,
            full_features=full_features,
            train_labels=train_frame[LABEL_COLUMN].to_numpy(),
            test_labels=test_frame[LABEL_COLUMN].to_numpy(),
            feature_names=tabular_names + embedding_names,
            train_index=train_index,
            test_index=test_index,
            mode="embedding",
        )

    @staticmethod
    def _build_tabular_transformer(dense_output: bool) -> ColumnTransformer:
        return ColumnTransformer(
            transformers=[
                (
                    "numeric",
                    Pipeline([("scaler", StandardScaler())]),
                    NUMERIC_FEATURES,
                ),
                (
                    "categorical",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=not dense_output),
                    CATEGORICAL_FEATURES,
                ),
            ],
            remainder="drop",
            sparse_threshold=0.0 if dense_output else 0.3,
        )

