from __future__ import annotations

import argparse
import json

from .config import get_settings
from .llm import SiliconFlowClient
from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cross-border animal disease intelligence mining and prediction toolkit.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the end-to-end pipeline.")
    run_parser.add_argument("--input", required=True, help="Input CSV/XLSX dataset path.")
    run_parser.add_argument("--output", default=None, help="Output directory.")
    run_parser.add_argument(
        "--llm-mode",
        default="auto",
        choices=["auto", "heuristic", "siliconflow"],
        help="Choose LLM extraction mode.",
    )
    run_parser.add_argument(
        "--disable-embeddings",
        action="store_true",
        help="Disable SiliconFlow embeddings even when API key exists.",
    )

    models_parser = subparsers.add_parser("list-models", help="List available SiliconFlow models.")
    models_parser.add_argument(
        "--sub-type",
        default=None,
        choices=["chat", "embedding", "reranker"],
        help="Optional sub_type filter.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        summary = run_pipeline(
            input_path=args.input,
            output_dir=args.output,
            llm_mode=args.llm_mode,
            use_embeddings=not args.disable_embeddings,
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
        embedding_model=settings.embedding_model,
        timeout=settings.request_timeout,
    )
    models = client.list_models(sub_type=args.sub_type)
    print(json.dumps(models, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
