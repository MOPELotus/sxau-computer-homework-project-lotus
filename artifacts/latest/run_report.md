# 跨境动物疫病情报分析阶段性简报

- 生成时间：2026-03-28 21:13:22
- 资料来源路径：materials\source
- 情报抽取模式：规则回退模式
- 特征融合方式：结构化特征 + TF-IDF 文本特征
- 风险评分方式：监督学习
- 已处理资料数：2
- 跳过资料数：0
- 生成记录数：9

## 模型指标

- Accuracy: 1.0
- Precision: 1.0
- Recall: 1.0
- F1: 1.0
- ROC-AUC: 1.0

## 建议上传到协作平台的结果

- standardized_dataset.csv：资料自动归一化后的标准数据表
- processed_dataset.csv：加入大模型情报抽取结果后的分析表
- predictions.csv：全量记录的跨境风险概率与等级
- feature_importance.csv：特征重要性结果
- ingest_report.json：资料处理与跳过情况说明
- risk_trend.png：风险趋势图
- disease_risk_rank.png：疾病风险排序图
- feature_importance.png：重要特征柱状图

## 图表路径

- risk_trend: artifacts\latest\risk_trend.png
- disease_risk_rank: artifacts\latest\disease_risk_rank.png
- feature_importance: artifacts\latest\feature_importance.png
