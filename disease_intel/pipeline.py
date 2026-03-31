from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .config import get_settings
from .features import FusionFeatureBuilder
from .ingest import load_dataset_from_source
from .llm import SiliconFlowClient
from .mining import IntelligenceMiner
from .model import DiseaseRiskModel
from .visualization import create_figures


def run_pipeline(
    source_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    llm_mode: str = "auto",
) -> dict[str, object]:
    settings = get_settings()
    actual_source = Path(source_path) if source_path else settings.default_materials_dir
    destination = Path(output_dir) if output_dir else settings.default_output_dir
    destination.mkdir(parents=True, exist_ok=True)

    client = _build_client(settings, llm_mode)
    standardized_dataset, ingest_report = load_dataset_from_source(actual_source, client=client)
    miner = IntelligenceMiner(client=client)
    mined_dataset = miner.mine_frame(standardized_dataset)

    feature_pack = FusionFeatureBuilder().build(mined_dataset)
    artifacts = DiseaseRiskModel().fit(feature_pack, mined_dataset)
    figures = create_figures(artifacts.full_predictions, artifacts.feature_importance, destination)

    standardized_path = destination / "standardized_dataset.csv"
    processed_path = destination / "processed_dataset.csv"
    predictions_path = destination / "predictions.csv"
    test_predictions_path = destination / "test_predictions.csv"
    importance_path = destination / "feature_importance.csv"
    metrics_path = destination / "metrics.json"
    ingest_report_path = destination / "ingest_report.json"
    report_path = destination / "run_report.md"

    standardized_dataset.to_csv(standardized_path, index=False, encoding="utf-8-sig")
    mined_dataset.to_csv(processed_path, index=False, encoding="utf-8-sig")
    artifacts.full_predictions.to_csv(predictions_path, index=False, encoding="utf-8-sig")
    artifacts.test_predictions.to_csv(test_predictions_path, index=False, encoding="utf-8-sig")
    artifacts.feature_importance.to_csv(importance_path, index=False, encoding="utf-8-sig")
    metrics_path.write_text(json.dumps(artifacts.metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    ingest_report_path.write_text(json.dumps(ingest_report, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_report(
        report_path=report_path,
        source_path=actual_source,
        llm_mode="siliconflow" if client is not None else "heuristic",
        feature_mode=feature_pack.mode,
        model_mode=artifacts.mode,
        metrics=artifacts.metrics,
        ingest_report=ingest_report,
        figures=figures,
    )

    return {
        "source_path": str(actual_source),
        "output_dir": str(destination),
        "llm_mode": "siliconflow" if client is not None else "heuristic",
        "feature_mode": feature_pack.mode,
        "model_mode": artifacts.mode,
        "metrics": artifacts.metrics,
        "files": {
            "standardized_dataset": str(standardized_path),
            "processed_dataset": str(processed_path),
            "predictions": str(predictions_path),
            "test_predictions": str(test_predictions_path),
            "feature_importance_csv": str(importance_path),
            "metrics": str(metrics_path),
            "ingest_report": str(ingest_report_path),
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
        timeout=settings.request_timeout,
    )


def _write_report(
    report_path: Path,
    source_path: Path,
    llm_mode: str,
    feature_mode: str,
    model_mode: str,
    metrics: dict[str, float | None | str],
    ingest_report: dict[str, object],
    figures: dict[str, str],
) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    llm_mode_label = {"siliconflow": "智能决策模型模式", "heuristic": "规则回退模式"}.get(llm_mode, llm_mode)
    model_mode_label = {"supervised": "监督学习预警模型", "score_only": "规则评分预警模型"}.get(
        model_mode, model_mode
    )
    report = f"""# 跨境重大动物疫病预警分析阶段性简报

- 生成时间：{timestamp}
- 资料来源路径：{source_path}
- 大数据清洗与解析模式：{llm_mode_label}
- 多维预警指标构建方式：{feature_mode}
- 预警评分方式：{model_mode_label}
- 已处理资料数：{ingest_report["processed_file_count"]}
- 跳过资料数：{ingest_report["skipped_file_count"]}
- 生成记录数：{ingest_report["record_count"]}

## 模型指标

- Accuracy: {metrics.get("accuracy")}
- Precision: {metrics.get("precision")}
- Recall: {metrics.get("recall")}
- F1: {metrics.get("f1")}
- ROC-AUC: {metrics.get("roc_auc")}

## 建议上传到协作平台的结果

- standardized_dataset.csv：资料自动归一化后的标准数据表
- processed_dataset.csv：加入智能决策模型解析结果后的分析表
- predictions.csv：全量记录的预警概率与等级
- feature_importance.csv：多维预警指标重要性结果
- ingest_report.json：资料处理与跳过情况说明
- risk_trend.png：预警趋势图
- disease_risk_rank.png：疫病预警风险排序图
- feature_importance.png：关键预警特征柱状图

## 图表路径

- risk_trend: {figures["risk_trend"]}
- disease_risk_rank: {figures["disease_risk_rank"]}
- feature_importance: {figures["feature_importance_figure"]}
"""
    report_path.write_text(report, encoding="utf-8")
