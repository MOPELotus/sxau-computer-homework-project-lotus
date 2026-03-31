from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


plt.style.use("seaborn-v0_8")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False


def create_figures(
    predictions: pd.DataFrame,
    feature_importance: pd.DataFrame,
    output_dir: Path,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    risk_trend_path = output_dir / "risk_trend.png"
    disease_rank_path = output_dir / "disease_risk_rank.png"
    importance_path = output_dir / "feature_importance.png"

    _plot_risk_trend(predictions, risk_trend_path)
    _plot_disease_risk_rank(predictions, disease_rank_path)
    _plot_feature_importance(feature_importance, importance_path)

    return {
        "risk_trend": str(risk_trend_path),
        "disease_risk_rank": str(disease_rank_path),
        "feature_importance_figure": str(importance_path),
    }


def _plot_risk_trend(predictions: pd.DataFrame, output_path: Path) -> None:
    frame = predictions.copy()
    frame["report_date"] = pd.to_datetime(frame["report_date"])
    trend = frame.groupby("report_date", as_index=False)["risk_probability"].mean()

    plt.figure(figsize=(10, 5))
    plt.plot(trend["report_date"], trend["risk_probability"], marker="o", linewidth=2.2, color="#1b5e20")
    plt.fill_between(trend["report_date"], trend["risk_probability"], alpha=0.18, color="#66bb6a")
    plt.title("跨境重大动物疫病预警趋势")
    plt.xlabel("报告日期")
    plt.ylabel("平均风险概率")
    plt.ylim(0, 1)
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_disease_risk_rank(predictions: pd.DataFrame, output_path: Path) -> None:
    ranking = (
        predictions.groupby("disease", as_index=False)["risk_probability"]
        .mean()
        .sort_values("risk_probability", ascending=True)
    )

    plt.figure(figsize=(9, 5))
    plt.barh(ranking["disease"], ranking["risk_probability"], color="#ef6c00")
    plt.title("不同疫病平均预警风险排序")
    plt.xlabel("平均风险概率")
    plt.xlim(0, 1)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_feature_importance(feature_importance: pd.DataFrame, output_path: Path) -> None:
    top_features = feature_importance.head(12).sort_values("importance", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(top_features["feature"], top_features["importance"], color="#1565c0")
    plt.title("关键预警特征重要性")
    plt.xlabel("重要性值")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
