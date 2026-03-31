from __future__ import annotations

import argparse
import json

from .config import get_settings
from .llm import SiliconFlowClient
from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="跨境重大动物疫病大数据预警分析工具。",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="运行资料归一化、大数据清洗与解析和风险预测全流程。")
    run_parser.add_argument(
        "--input",
        default=None,
        help="资料文件或资料目录路径；不传时默认使用 materials/source。",
    )
    run_parser.add_argument("--output", default=None, help="输出目录。")
    run_parser.add_argument(
        "--llm-mode",
        default="auto",
        choices=["auto", "heuristic", "siliconflow"],
        help="选择智能决策模型分析模式。",
    )

    models_parser = subparsers.add_parser("list-models", help="列出可用的 SiliconFlow 模型。")
    models_parser.add_argument(
        "--sub-type",
        default=None,
        choices=["chat", "embedding", "reranker"],
        help="可选的 sub_type 过滤条件。",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        summary = run_pipeline(
            source_path=args.input,
            output_dir=args.output,
            llm_mode=args.llm_mode,
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    settings = get_settings()
    if not settings.api_enabled:
        raise SystemExit("未配置 SILICONFLOW_API_KEY，无法拉取模型列表。")

    client = SiliconFlowClient(
        api_key=settings.api_key,
        base_url=settings.api_base_url,
        chat_model=settings.chat_model,
        timeout=settings.request_timeout,
    )
    models = client.list_models(sub_type=args.sub_type)
    print(json.dumps(models, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
