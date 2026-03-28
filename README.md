# 大语言模型驱动的跨境动物疫病情报挖掘与多特征融合预测研究

这是按你们小组作业“组长职责”直接落成的可运行 Python 项目，覆盖以下内容：

- Python 项目环境说明与依赖清单
- SiliconFlow 大模型接口接入
- 原始疫情数据清洗与标准化
- LLM 驱动的文本情报抽取
- 多特征融合风险预测
- 可视化图表与交接材料输出

项目默认支持两种运行模式：

- 有 `SILICONFLOW_API_KEY`：调用 SiliconFlow 完成文本情报抽取，并可选使用嵌入向量
- 没有 `SILICONFLOW_API_KEY`：自动切换到规则抽取 + TF-IDF 融合模式，保证 demo 可以直接跑通

## 1. 目录结构

```text
.
|-- disease_intel/                # 核心代码
|-- data/
|   |-- raw/                      # 后续放杜毅达采集的官方原始数据
|   |-- processed/                # 处理中间结果
|   `-- sample/                   # 可直接演示的示例数据
|-- artifacts/                    # 运行后输出的图表、指标、预测结果
|-- docs/                         # 交接说明
|-- tests/                        # 冒烟测试
|-- requirements.txt
|-- .env.example
`-- run_demo.ps1
```

## 2. 本地运行

不使用虚拟环境，直接在本机 Python 环境执行即可。

```powershell
pip install -r requirements.txt
Copy-Item .env.example .env
python -m disease_intel.cli run --input data/sample/outbreak_events_sample.csv --output artifacts/latest
```

也可以直接执行：

```powershell
.\run_demo.ps1
```

## 3. SiliconFlow 配置

在 `.env` 中填写：

```env
SILICONFLOW_API_KEY=你的硅基流动API密钥
SILICONFLOW_CHAT_MODEL=Qwen/Qwen3.5-27B
SILICONFLOW_EMBEDDING_MODEL=Qwen/Qwen3-Embedding-8B
```

代码对接的是 SiliconFlow 官方 OpenAI 兼容接口：

- `POST https://api.siliconflow.cn/v1/chat/completions`
- `POST https://api.siliconflow.cn/v1/embeddings`
- `GET https://api.siliconflow.cn/v1/models`

## 4. 输出结果

运行后会在 `artifacts/latest` 下生成：

- `processed_dataset.csv`：加入情报抽取结果后的清洗数据
- `predictions.csv`：每条疫情记录的跨境风险概率与等级
- `test_predictions.csv`：测试集预测结果
- `metrics.json`：准确率、召回率、F1、ROC-AUC
- `feature_importance.csv`：模型重要特征
- `risk_trend.png`：风险趋势图
- `disease_risk_rank.png`：不同疫病平均风险图
- `feature_importance.png`：重要特征图
- `run_report.md`：适合上传协作平台的简报

## 5. 推荐工作流

1. 杜毅达把官方数据放入 `data/raw/`
2. 组长将原始数据整理成与示例文件一致的字段结构
3. 执行预测流程，生成图表与指标
4. 将 `artifacts/latest` 中的结果上传到协作平台“公共情报资料库”
5. 张静云和丁俊心分别下载图表、结果表和简报用于论文及 PPT

## 6. 组长职责映射

- Python 环境搭建：`requirements.txt`、`.env.example`、`run_demo.ps1`
- LLM API 调用：`disease_intel/llm.py`
- 数据处理：`disease_intel/data.py`、`disease_intel/mining.py`
- 算法实现：`disease_intel/features.py`、`disease_intel/model.py`
- 实验截图与图表：运行后生成到 `artifacts/latest`

## 7. 测试

```powershell
python -m unittest tests/test_pipeline.py
```

## 8. 说明

- 示例数据为课程演示用的官方通报风格样本，后续可直接替换为真实采集数据
- 若启用真实 API，但某次请求失败，程序会自动退回到规则抽取模式，避免整条流程中断

