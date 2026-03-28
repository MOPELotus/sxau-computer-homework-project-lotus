from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .llm import SiliconFlowAPIError, SiliconFlowClient


BORDER_TERMS = [
    "border",
    "cross-border",
    "cross border",
    "port",
    "trade corridor",
    "checkpoint",
    "movement",
    "transport",
    "truck",
    "market",
    "边境",
    "跨境",
    "口岸",
    "通道",
    "运输",
    "车辆",
    "市场",
    "交易",
]
SPREAD_TERMS = [
    "rapid spread",
    "cluster",
    "multiple farms",
    "migratory",
    "wild birds",
    "shared grazing",
    "long-distance",
    "transboundary",
    "new district",
    "扩散",
    "传播",
    "多个",
    "多点",
    "候鸟",
    "迁徙",
    "周边乡镇",
    "多家养殖场",
]
CONTROL_TERMS = [
    "delayed",
    "insufficient",
    "limited surveillance",
    "vaccination gap",
    "biosecurity weakness",
    "culling",
    "movement restriction",
    "late detection",
    "informal trade",
    "延迟",
    "不足",
    "监测薄弱",
    "免疫缺口",
    "生物安全薄弱",
    "扑杀",
    "移动限制",
    "晚发现",
    "非正规贸易",
]


class IntelligenceMiner:
    def __init__(self, client: SiliconFlowClient | None = None) -> None:
        self.client = client

    def mine_frame(self, dataset: pd.DataFrame) -> pd.DataFrame:
        records: list[dict[str, Any]] = []
        for _, row in dataset.iterrows():
            if self.client is None:
                records.append(self._mine_with_rules(row))
                continue

            try:
                records.append(self._mine_with_llm(row))
            except SiliconFlowAPIError:
                records.append(self._mine_with_rules(row))

        mined = pd.DataFrame(records)
        result = pd.concat([dataset.reset_index(drop=True), mined], axis=1)
        result["intel_risk_score"] = np.clip(
            (
                0.35 * result["llm_border_relevance"]
                + 0.25 * result["llm_transmission_complexity"]
                + 0.25 * result["llm_control_pressure"]
                + 0.15 * np.clip(result["neighboring_outbreaks_14d"], 0, 10)
            )
            / 10,
            0,
            1,
        )
        return result

    def _mine_with_llm(self, row: pd.Series) -> dict[str, Any]:
        system_prompt = (
            "你是动物疫病情报分析助手。"
            "请基于输入的疫情通报，以 JSON 对象返回分析结果，不要输出多余解释。"
        )
        user_prompt = f"""
请分析以下跨境动物疫病情报，并输出 JSON：
{{
  "summary_zh": "不超过80字的中文摘要",
  "border_relevance": 0-10整数,
  "transmission_complexity": 0-10整数,
  "control_pressure": 0-10整数,
  "key_signals": ["最多4个关键词"],
  "recommended_action": "一句中文建议"
}}

事件信息：
- 日期: {row["report_date"].date()}
- 来源平台: {row["source_platform"]}
- 国家: {row["country"]}
- 边境区域: {row["border_region"]}
- 疫病: {row["disease"]}
- 宿主: {row["host_species"]}
- 发病数: {row["cases"]}
- 死亡数: {row["deaths"]}
- 扑杀数: {row["culling"]}
- 14日周边疫情数: {row["neighboring_outbreaks_14d"]}
- 贸易流指数: {row["trade_flow_index"]}
- 交通可达性: {row["transport_access_index"]}
- 距边境距离(km): {row["border_distance_km"]}
- 降雨异常: {row["rainfall_anomaly"]}
- 温度异常: {row["temperature_anomaly"]}
- 文本通报: {row["narrative_text"]}
""".strip()

        payload, _ = self.client.chat_json(system_prompt=system_prompt, user_prompt=user_prompt)
        summary = str(payload.get("summary_zh", "")).strip() or "模型未返回摘要"
        key_signals = payload.get("key_signals", [])
        if not isinstance(key_signals, list):
            key_signals = [str(key_signals)]

        return {
            "llm_mode": "siliconflow",
            "llm_summary": summary,
            "llm_border_relevance": self._clamp_score(payload.get("border_relevance")),
            "llm_transmission_complexity": self._clamp_score(payload.get("transmission_complexity")),
            "llm_control_pressure": self._clamp_score(payload.get("control_pressure")),
            "llm_key_signals": ", ".join(str(item) for item in key_signals[:4]),
            "llm_recommended_action": str(payload.get("recommended_action", "")).strip(),
        }

    def _mine_with_rules(self, row: pd.Series) -> dict[str, Any]:
        text = str(row["narrative_text"]).lower()
        border_hits = self._count_terms(text, BORDER_TERMS)
        spread_hits = self._count_terms(text, SPREAD_TERMS)
        control_hits = self._count_terms(text, CONTROL_TERMS)

        border_score = min(
            10,
            int(
                2
                + border_hits * 2
                + (row["trade_flow_index"] / 30)
                + (row["transport_access_index"] / 40)
                + (1 if row["border_distance_km"] < 150 else 0)
            ),
        )
        transmission_score = min(
            10,
            int(
                2
                + spread_hits * 2
                + np.log1p(row["cases"])
                + (row["neighboring_outbreaks_14d"] / 2)
            ),
        )
        control_score = min(
            10,
            int(
                2
                + control_hits * 2
                + (row["culling"] > 0)
                + (row["deaths"] > row["cases"] * 0.08)
            ),
        )

        signals: list[str] = []
        if border_hits:
            signals.append("border traffic")
        if spread_hits:
            signals.append("multi-point spread")
        if row["neighboring_outbreaks_14d"] >= 4:
            signals.append("regional clustering")
        if row["border_distance_km"] < 120:
            signals.append("near border")
        if row["trade_flow_index"] >= 75:
            signals.append("high trade flow")

        summary = (
            f"{row['country']} {row['border_region']} 出现{row['disease']}疫情，"
            f"跨境相关性评分为{border_score}/10。"
        )

        if row["cross_border_alert"] == 1:
            action = "建议提高口岸监测频次并同步排查运输链。"
        else:
            action = "建议保持常规监测，并继续跟踪周边疫情变化。"

        return {
            "llm_mode": "heuristic",
            "llm_summary": summary,
            "llm_border_relevance": border_score,
            "llm_transmission_complexity": transmission_score,
            "llm_control_pressure": control_score,
            "llm_key_signals": ", ".join(signals[:4]),
            "llm_recommended_action": action,
        }

    @staticmethod
    def _clamp_score(value: Any) -> int:
        try:
            number = int(float(value))
        except (TypeError, ValueError):
            return 0
        return max(0, min(10, number))

    @staticmethod
    def _count_terms(text: str, terms: list[str]) -> int:
        return sum(1 for term in terms if term in text)
