from __future__ import annotations

import argparse
import json

from .crawler import fetch_documents_from_urls, load_documents_from_json
from .indexer import PageIndexer


def _build_command(args: argparse.Namespace) -> None:
    docs = []
    if args.input:
        docs.extend(load_documents_from_json(args.input))
    if args.url:
        docs.extend(fetch_documents_from_urls(args.url, timeout_s=args.timeout))

    if not docs:
        raise SystemExit("No documents provided. Use --input and/or --url.")

    indexer = PageIndexer(chunk_size_words=args.chunk_size, overlap_words=args.overlap)
    indexer.build(docs)
    indexer.save(args.output_dir)

    print(f"Built index with {len(indexer.chunks)} chunks at: {args.output_dir}")


def _query_command(args: argparse.Namespace) -> None:
    indexer = PageIndexer()
    indexer.load(args.index_dir)
    results = indexer.query(args.text, top_k=args.top_k)
    print(json.dumps(results, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Practical PageIndex-style example CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="Build index from JSON and/or URLs")
    build.add_argument("--input", type=str, help="Path to JSON array of page documents")
    build.add_argument("--url", action="append", help="Source URL to crawl", default=[])
    build.add_argument("--timeout", type=int, default=15, help="URL request timeout seconds")
    build.add_argument("--chunk-size", type=int, default=120)
    build.add_argument("--overlap", type=int, default=20)
    build.add_argument("--output-dir", type=str, required=True)
    build.set_defaults(func=_build_command)

    query = sub.add_parser("query", help="Query an existing index")
    query.add_argument("--index-dir", type=str, required=True)
    query.add_argument("--text", type=str, required=True)
    query.add_argument("--top-k", type=int, default=5)
    query.set_defaults(func=_query_command)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
