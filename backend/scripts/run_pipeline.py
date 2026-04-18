"""
scripts/run_pipeline.py
------------------------
Command-line entry point. Run from the project root:

    python scripts/run_pipeline.py

Or with a topic directly:

    python scripts/run_pipeline.py --topic "quantum computing"
"""

import sys
import os
import argparse
import logging

# Make sure imports resolve from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

from src.pipeline.research_pipeline import run


def main():
    parser = argparse.ArgumentParser(description="AI Research Agent")
    parser.add_argument("--topic", type=str, default=None,
                        help="Research topic (prompted if omitted)")
    parser.add_argument("--fresh", action="store_true",
                        help="Force re-fetch, ignore cache")
    args = parser.parse_args()

    topic = args.topic or input("Enter research topic: ").strip()
    if not topic:
        print("No topic provided. Exiting.")
        sys.exit(1)

    result = run(topic, force_refresh=args.fresh)

    print("\n" + "="*60)
    print(f"  RESEARCH REPORT: {result['topic'].upper()}")
    print("="*60)
    print(result["report"])
    print("="*60)

    if result.get("cached"):
        print("(Served from cache — use --fresh to regenerate)")

    print(f"\nSources: {len(result['sources'])}")
    for s in result["sources"]:
        print(f"  [{s.get('source_type','?')}] {s.get('title','?')}")
        print(f"         {s.get('url','')}")


if __name__ == "__main__":
    main()
