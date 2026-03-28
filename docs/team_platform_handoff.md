# 协作平台交接说明

本项目建议采用“统一资料目录 + 统一结果目录 + 平台统一上传”的交接方式。

## 资料投放

所有待分析资料统一放入 `materials/source`，不要求组员先手工改成固定示例格式。程序会自动完成：

- 资料扫描
- 表头识别与字段映射
- 文本资料抽取
- 图片视觉识别
- PDF/Office 文档文本提取或转换
- 标准化数据生成
- 风险评分与图表输出

## 建议上传的结果

每次运行后，建议将以下文件上传至协作平台“公共情报资料库”：

- `artifacts/latest/standardized_dataset.csv`
- `artifacts/latest/processed_dataset.csv`
- `artifacts/latest/predictions.csv`
- `artifacts/latest/feature_importance.csv`
- `artifacts/latest/metrics.json`
- `artifacts/latest/ingest_report.json`
- `artifacts/latest/run_report.md`
- `artifacts/latest/risk_trend.png`
- `artifacts/latest/disease_risk_rank.png`
- `artifacts/latest/feature_importance.png`

## 组员使用建议

- 张静云：重点下载 `run_report.md`、`metrics.json`、三张图和 `predictions.csv`
- 丁俊心：重点下载三张图、`run_report.md` 和 `predictions.csv`
- 鲍木梓：重点下载论文终稿，不需要改动代码产出的数据文件
- 谢思凡：重点下载最终图表、论文和 PPT，用于视频脚本与剪辑素材整理

## 注意事项

- 无法成功提取的资料会被登记到 `ingest_report.json`
- `doc`、`ppt` 等旧版 Office 文件会优先尝试自动转换为 PDF 再解析
