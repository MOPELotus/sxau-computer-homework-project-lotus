# 协作平台交接建议

建议组长每次完成实验后，将以下文件统一上传到 `公共情报资料库`：

- `artifacts/latest/processed_dataset.csv`
- `artifacts/latest/predictions.csv`
- `artifacts/latest/metrics.json`
- `artifacts/latest/run_report.md`
- `artifacts/latest/risk_trend.png`
- `artifacts/latest/disease_risk_rank.png`
- `artifacts/latest/feature_importance.png`

## 对应组员使用方式

- 张静云：下载 `run_report.md`、`metrics.json`、全部图表，用于论文技术实现和实验结果章节
- 丁俊心：下载三张图和 `predictions.csv`，整理成 5 个标准模块的 PPT
- 谢思凡：下载最终定稿图表和论文，用于视频脚本与后期素材
- 鲍木梓：下载论文正文后进行版式统一，不必修改代码产出表

## 推荐上传节奏

1. 原始数据到位后，先上传一次 `processed_dataset.csv`
2. 训练完成后，再补传 `metrics.json`、`predictions.csv` 和三张图
3. 提交前一天，将完整 `artifacts/latest` 重新覆盖上传一次，确保全组拿到最新版本

