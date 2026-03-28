# 组长阶段性技术产出简报

- 生成时间：2026-03-28 20:39:56
- 输入数据：data\sample\outbreak_events_sample.csv
- 情报抽取模式：heuristic
- 特征融合模式：tfidf

## 测试集指标

- Accuracy: 1.0
- Precision: 1.0
- Recall: 1.0
- F1: 1.0
- ROC-AUC: 1.0

## 建议上传到协作平台的结果

- processed_dataset.csv：清洗后并附带情报抽取结果的数据表
- predictions.csv：全量记录的跨境风险概率与等级
- feature_importance.csv：模型重要特征
- risk_trend.png：趋势图
- disease_risk_rank.png：疾病风险排序图
- feature_importance.png：重要特征柱状图

## 图表路径

- risk_trend: artifacts\latest\risk_trend.png
- disease_risk_rank: artifacts\latest\disease_risk_rank.png
- feature_importance: artifacts\latest\feature_importance.png
