# 大数据与智能模型在跨境重大动物疫病预警中的应用分析

本仓库用于支撑课程项目《大数据与智能模型在跨境重大动物疫病预警中的应用分析》的技术实现，覆盖资料归一化、大数据清洗与解析、多维预警指标构建、风险预测、结果可视化与协作交接等环节。

## 项目定位

本项目面向小组作业中的技术主线，目标是把分散的跨境疫病资料自动整理为统一大数据资产，并输出可直接用于论文、PPT 和平台交接的预警分析结果。

当前版本采用以下原则：

- 默认模型统一为 `Qwen/Qwen3.5-397B-A17B`，作为核心智能决策模型接入
- 默认入口统一为资料文件夹 `materials/source`
- 资料无需先手工整理成示例表，再由程序执行自动筛选、字段映射、文本抽取、结构化解析与预警分析
- 对支持视觉输入的资料，优先使用同一模型执行视觉理解与结构化解析
- 若未配置 `SILICONFLOW_API_KEY`，系统会退回规则模式，保证本地 demo 仍可运行

## 术语口径

为便于论文、PPT 与视频脚本统一表述，建议按以下口径引用本项目：

- `情报抽取` 对外统一表述为 `大数据清洗与解析`
- `多特征融合` 对外统一表述为 `多维预警指标构建`
- `LLM` 或 `大模型` 对外统一表述为 `智能决策模型`
- 代码包名 `disease_intel` 与部分内部字段名保持不变，仅作为技术实现标识

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

仓库内已经附带一套完整示例，位于 `materials/source/全格式示例包`，覆盖上述全部格式。
如需重新生成，可执行：

```powershell
.\tools\generate_sample_materials.ps1
```

程序会自动完成以下处理：

1. 扫描资料目录
2. 识别表格或文本资料
3. 对 Word、PPT、PDF 优先提取文本；必要时执行转换或图片化处理
4. 自动映射字段到标准疫情结构
5. 调用智能决策模型完成大数据清洗与解析，提炼预警摘要与风险信号
6. 进行多维预警指标构建与风险评分
7. 输出图表、数据表和阶段简报

## 关于图片和 PDF

当前项目按“全流程统一使用 `Qwen/Qwen3.5-397B-A17B` 作为智能决策模型”的要求配置。现在图片会通过 `chat/completions` 的视觉输入方式直接送入同一模型；PDF 会优先提取文本，提取不足时再转成页面图片送入视觉输入。

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
python -m disease_intel.cli run --input "materials/source/全格式示例包" --output artifacts/latest
```

若要处理你自己的资料目录：

```powershell
python -m disease_intel.cli run --input materials/source --output artifacts/latest_api
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
- `processed_dataset.csv`：加入智能决策模型解析结果后的分析数据表
- `predictions.csv`：每条记录的预警概率和风险等级
- `test_predictions.csv`：监督模式下的测试集预测结果
- `feature_importance.csv`：多维预警指标重要性结果
- `metrics.json`：指标文件
- `ingest_report.json`：资料扫描、处理和跳过情况
- `risk_trend.png`：预警趋势图
- `disease_risk_rank.png`：疫病预警风险排序图
- `feature_importance.png`：关键预警特征重要性图
- `run_report.md`：适合上传协作平台的阶段性简报

## 协作平台交接建议

建议每次运行后，将 `artifacts/latest` 内的核心产出统一上传到协作平台“公共情报资料库”，作为项目“大数据采样”与“预警分析结果”的统一交接目录，供论文撰写、PPT 制作和视频录制环节同步调用。

## 测试

```powershell
python -m unittest tests/test_pipeline.py
```
