# 跨境重大动物疫病预警分析阶段性简报

- 生成时间：2026-03-31 13:09:23
- 资料来源路径：materials\source\全格式示例包
- 大数据清洗与解析模式：智能决策模型模式
- 多维预警指标构建方式：结构化大数据特征 + TF-IDF 文本语义特征
- 预警评分方式：监督学习预警模型
- 已处理资料数：16
- 跳过资料数：0
- 生成记录数：19

## 模型指标

- Accuracy: 1.0
- Precision: 1.0
- Recall: 1.0
- F1: 1.0
- ROC-AUC: 1.0

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

- risk_trend: artifacts\latest\risk_trend.png
- disease_risk_rank: artifacts\latest\disease_risk_rank.png
- feature_importance: artifacts\latest\feature_importance.png
