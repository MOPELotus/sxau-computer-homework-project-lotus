from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


EXPECTED_COLUMNS = [
    "event_id",
    "report_date",
    "source_platform",
    "country",
    "border_region",
    "disease",
    "host_species",
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
    "narrative_text",
    "cross_border_alert",
]

NUMERIC_COLUMNS = [
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
]

CATEGORICAL_COLUMNS = [
    "source_platform",
    "country",
    "border_region",
    "disease",
    "host_species",
]

TEXT_COLUMN = "narrative_text"
LABEL_COLUMN = "cross_border_alert"


def load_outbreak_dataset(path: str | Path) -> pd.DataFrame:
    input_path = Path(path)
    if not input_path.exists():
        raise FileNotFoundError(f"Dataset not found: {input_path}")

    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        frame = pd.read_csv(input_path)
    elif suffix in {".xlsx", ".xls"}:
        frame = pd.read_excel(input_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    return normalize_dataset(frame)


def normalize_dataset(frame: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    dataset = frame.copy()
    dataset["report_date"] = pd.to_datetime(dataset["report_date"], errors="coerce")
    if dataset["report_date"].isna().any():
        raise ValueError("report_date contains invalid values")

    for column in NUMERIC_COLUMNS + [LABEL_COLUMN]:
        dataset[column] = pd.to_numeric(dataset[column], errors="coerce").fillna(0)

    for column in CATEGORICAL_COLUMNS:
        dataset[column] = dataset[column].fillna("Unknown").astype(str).str.strip()

    dataset[TEXT_COLUMN] = dataset[TEXT_COLUMN].fillna("").astype(str).str.strip()
    dataset["event_id"] = dataset["event_id"].astype(str).str.strip()
    dataset[LABEL_COLUMN] = dataset[LABEL_COLUMN].astype(int)

    dataset["case_fatality_rate"] = np.where(
        dataset["cases"] > 0,
        dataset["deaths"] / dataset["cases"],
        0.0,
    )
    dataset["outbreak_pressure"] = (
        np.log1p(dataset["cases"]) + np.log1p(dataset["neighboring_outbreaks_14d"])
    )
    dataset["border_proximity_score"] = np.clip(
        1 - (dataset["border_distance_km"] / 500),
        0,
        1,
    )

    dataset = dataset.sort_values("report_date").reset_index(drop=True)
    return dataset

