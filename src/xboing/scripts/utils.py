"""Utility functions for argument parsing, path validation, and summary logging for XBoing scripts."""

import argparse
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


def parse_input_output_args(parser, default_input: str, default_output: str):
    """Add standard input/output/dry-run arguments to an argparse parser."""
    parser.add_argument(
        "--input",
        "-i",
        default=default_input,
        help=f"Input directory (default: {default_input})",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=default_output,
        help=f"Output directory (default: {default_output})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be converted, but do not actually convert.",
    )
    return parser


def resolve_and_validate_paths(
    input_path: Path, output_path: Path, logger: Any
) -> tuple[Path, Path, bool]:
    """Resolve and validate input/output paths. Returns (input_path, output_path, valid)."""
    input_path = input_path.resolve()
    output_path = output_path.resolve()
    if not input_path.exists() or not input_path.is_dir():
        logger.error(
            f"[ERROR] Input directory {input_path} does not exist or is not a directory."
        )
        return input_path, output_path, False
    return input_path, output_path, True


def print_conversion_summary(logger: Any, results: Dict[str, List[str]]):
    """Log a summary of converted, skipped, and failed files."""
    logger.info("\nSummary:")
    logger.info(f"  Converted: {len(results['converted'])}")
    logger.info(f"  Skipped:   {len(results['skipped'])}")
    logger.info(f"  Failed:    {len(results['failed'])}")
    if results["failed"]:
        logger.info("  Failed files:")
        for f in results["failed"]:
            logger.info(f"    - {f}")


def run_cli_conversion(
    parser: argparse.ArgumentParser,
    default_input: str,
    default_output: str,
    logger: Any,
    conversion_func: Callable,
    summary_func: Optional[Callable] = None,
) -> int:
    """Standardized CLI entrypoint for conversion scripts: parses args, validates paths, runs conversion, prints summary."""
    parse_input_output_args(parser, default_input, default_output)
    args = parser.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    input_path, output_path, valid = resolve_and_validate_paths(
        input_path, output_path, logger
    )
    if not valid:
        return 1
    logger.info(f"Input:  {input_path}")
    logger.info(f"Output: {output_path}")
    logger.info(
        f"Mode:   {'DRY-RUN' if getattr(args, 'dry_run', False) else 'CONVERT'}\\n"
    )
    results = conversion_func(
        input_path, output_path, dry_run=getattr(args, "dry_run", False)
    )
    if summary_func:
        summary_func(logger, results)
    return 0
