from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .config import get_settings
from .data import load_outbreak_dataset
from .features import FusionFeatureBuilder
from .llm import SiliconFlowClient
from .mining import IntelligenceMiner
from .model import DiseaseRiskModel
from .visualization import create_figures


def run_pipeline(
    input_path: str | Path,
    output_dir: str | Path | None = None,
    llm_mode: str = "auto",
    use_embeddings: bool = True,
) -> dict[str, object]:
    settings = get_settings()
    destination = Path(output_dir) if output_dir else settings.default_output_dir
    destination.mkdir(parents=True, exist_ok=True)

    dataset = load_outbreak_dataset(input_path)
    client = _build_client(settings, llm_mode)
    miner = IntelligenceMiner(client=client)
    mined_dataset = miner.mine_frame(dataset)

    feature_mode = "tfidf"
    builder = FusionFeatureBuilder(client=client)
    if client is not None and use_embeddings:
        try:
            feature_pack = builder.build(mined_dataset, use_api_embeddings=True)
            feature_mode = feature_pack.mode
        except Exception:
            feature_pack = builder.build(mined_dataset, use_api_embeddings=False)
            feature_mode = feature_pack.mode
    else:
        feature_pack = builder.build(mined_dataset, use_api_embeddings=False)
        feature_mode = feature_pack.mode

    trainer = DiseaseRiskModel()
    artifacts = trainer.fit(feature_pack, mined_dataset)

    figures = create_figures(artifacts.full_predictions, artifacts.feature_importance, destination)

    processed_path = destination / "processed_dataset.csv"
    predictions_path = destination / "predictions.csv"
    test_predictions_path = destination / "test_predictions.csv"
    importance_path = destination / "feature_importance.csv"
    metrics_path = destination / "metrics.json"
    report_path = destination / "run_report.md"

    mined_dataset.to_csv(processed_path, index=False, encoding="utf-8-sig")
    artifacts.full_predictions.to_csv(predictions_path, index=False, encoding="utf-8-sig")
    artifacts.test_predictions.to_csv(test_predictions_path, index=False, encoding="utf-8-sig")
    artifacts.feature_importance.to_csv(importance_path, index=False, encoding="utf-8-sig")
    metrics_path.write_text(
        json.dumps(artifacts.metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _write_report(
        report_path=report_path,
        input_path=Path(input_path),
        llm_mode="siliconflow" if client is not None else "heuristic",
        feature_mode=feature_mode,
        metrics=artifacts.metrics,
        figures=figures,
    )

    return {
        "input_path": str(Path(input_path)),
        "output_dir": str(destination),
        "llm_mode": "siliconflow" if client is not None else "heuristic",
        "feature_mode": feature_mode,
        "metrics": artifacts.metrics,
        "files": {
            "processed_dataset": str(processed_path),
            "predictions": str(predictions_path),
            "test_predictions": str(test_predictions_path),
            "feature_importance_csv": str(importance_path),
            "metrics": str(metrics_path),
            "report": str(report_path),
            **figures,
        },
    }


def _build_client(settings, llm_mode: str) -> SiliconFlowClient | None:
    if llm_mode == "heuristic":
        return None
    if llm_mode == "siliconflow" and not settings.api_enabled:
        raise ValueError("llm_mode=siliconflow 但未配置 SILICONFLOW_API_KEY。")
    if llm_mode == "auto" and not settings.api_enabled:
        return None
    return SiliconFlowClient(
        api_key=settings.api_key,
        base_url=settings.api_base_url,
        chat_model=settings.chat_model,
        embedding_model=settings.embedding_model,
        timeout=settings.request_timeout,
    )


def _write_report(
    report_path: Path,
    input_path: Path,
    llm_mode: str,
    feature_mode: str,
    metrics: dict[str, float],
    figures: dict[str, str],
) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""# 组长阶段性技术产出简报

- 生成时间：{timestamp}
- 输入数据：{input_path}
- 情报抽取模式：{llm_mode}
- 特征融合模式：{feature_mode}

## 测试集指标

- Accuracy: {metrics["accuracy"]}
- Precision: {metrics["precision"]}
- Recall: {metrics["recall"]}
- F1: {metrics["f1"]}
- ROC-AUC: {metrics["roc_auc"]}

## 建议上传到协作平台的结果

- processed_dataset.csv：清洗后并附带情报抽取结果的数据表
- predictions.csv：全量记录的跨境风险概率与等级
- feature_importance.csv：模型重要特征
- risk_trend.png：趋势图
- disease_risk_rank.png：疾病风险排序图
- feature_importance.png：重要特征柱状图

## 图表路径

- risk_trend: {figures["risk_trend"]}
- disease_risk_rank: {figures["disease_risk_rank"]}
- feature_importance: {figures["feature_importance_figure"]}
"""
    report_path.write_text(report, encoding="utf-8")
