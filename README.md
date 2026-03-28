# 大语言模型驱动的跨境动物疫病情报挖掘与多特征融合预测研究

本仓库用于支撑课程项目《大语言模型驱动的跨境动物疫病情报挖掘与多特征融合预测研究》的技术实现，覆盖资料归一化、情报抽取、风险预测、结果可视化与协作交接等环节。

## 项目定位

本项目面向小组作业中的技术主线，目标是把分散的疫情资料自动整理为统一数据资产，并输出可直接用于论文、PPT 和平台交接的分析结果。

当前版本采用以下原则：

- 默认模型统一为 `Qwen/Qwen3.5-397B-A17B`
- 默认入口统一为资料文件夹 `materials/source`
- 资料无需先手工整理成示例表，再由程序执行自动筛选、字段映射、文本抽取与风险分析
- 对支持视觉输入的资料，优先使用同一模型执行视觉理解
- 若未配置 `SILICONFLOW_API_KEY`，系统会退回规则模式，保证本地 demo 仍可运行

## 目录结构

```text
.
|-- disease_intel/                # 核心代码
|-- materials/
|   `-- source/                   # 统一资料投放目录
|-- data/
|   |-- raw/                      # 保留原始数据目录
|   |-- processed/                # 中间数据目录
|   `-- sample/                   # 备用示例数据
|-- artifacts/                    # 图表、指标、预测结果
|-- docs/                         # 交接说明
|-- tests/                        # 冒烟测试
|-- requirements.txt
|-- .env.example
`-- run_demo.ps1
```

## 资料投放方式

将收集到的资料统一放入 `materials/source` 即可。当前版本支持：

- `.csv`
- `.xlsx`
- `.xls`
- `.txt`
- `.md`
- `.json`
- `.png`
- `.jpg`
- `.jpeg`
- `.webp`
- `.bmp`
- `.pdf`
- `.doc`
- `.docx`
- `.ppt`
- `.pptx`

程序会自动完成以下处理：

1. 扫描资料目录
2. 识别表格或文本资料
3. 对 Word、PPT、PDF 优先提取文本；必要时执行转换或图片化处理
4. 自动映射字段到标准疫情结构
5. 调用大模型抽取情报摘要与风险信号
6. 进行多特征融合风险评分
7. 输出图表、数据表和简报

## 关于图片和 PDF

当前项目按“全流程统一使用 `Qwen/Qwen3.5-397B-A17B`”的要求配置。现在图片会通过 `chat/completions` 的视觉输入方式直接送入同一模型；PDF 会优先提取文本，提取不足时再转成页面图片送入视觉输入。

也就是说：

- 文字类、表格类、图片类资料都已经纳入统一入口
- `doc/docx/ppt/pptx/pdf` 会先走提取或转换流程，实在无法处理时会登记到 `ingest_report.json`

## 本地运行

不使用虚拟环境，直接在本机 Python 环境执行即可。

```powershell
pip install -r requirements.txt
Copy-Item .env.example .env
.\run_demo.ps1
```

等价命令：

```powershell
python -m disease_intel.cli run --input materials/source --output artifacts/latest
```

## SiliconFlow 配置

在 `.env` 中填写：

```env
SILICONFLOW_API_KEY=你的硅基流动API密钥
SILICONFLOW_CHAT_MODEL=Qwen/Qwen3.5-397B-A17B
```

项目当前使用 SiliconFlow 官方兼容接口中的：

- `POST /v1/chat/completions`
- `POST /v1/files` 与 `POST /v1/batches` 可作为后续大批量离线处理扩展
- `GET /v1/models`

## 运行产出

运行结束后，`artifacts/latest` 中会生成：

- `standardized_dataset.csv`：资料自动归一化后的标准数据表
- `processed_dataset.csv`：加入情报抽取结果后的分析数据表
- `predictions.csv`：每条记录的风险概率和风险等级
- `test_predictions.csv`：监督模式下的测试集预测结果
- `feature_importance.csv`：特征重要性结果
- `metrics.json`：指标文件
- `ingest_report.json`：资料扫描、处理和跳过情况
- `risk_trend.png`：风险趋势图
- `disease_risk_rank.png`：疾病风险排序图
- `feature_importance.png`：关键特征重要性图
- `run_report.md`：适合上传协作平台的阶段简报

## 协作平台交接建议

建议每次运行后，将 `artifacts/latest` 内的核心产出统一上传到协作平台“公共情报资料库”，供论文撰写、PPT 制作和视频录制环节同步调用。

## 测试

```powershell
python -m unittest tests/test_pipeline.py
```
