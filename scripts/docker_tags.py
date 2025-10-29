# /// script
# dependencies = ["requests", "requests-cache"]
# requires-python = ">=3.9"
# ///

"""Get all tags from the Docker Hub."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import TYPE_CHECKING

import requests
import requests_cache

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

DEFAULT_TAGS = (
    "6.0.0-230405-apache",
    "6.2.0-230732-apache",
    "6.6.0-240729-apache",
    "6.15.20-251021-apache",
)
SKIP_TAGS = (
    "6.15.18-251016-apache",  # PATCH for question answers is broken
    "6.15.19-251017-apache",  # PATCH for question answers is broken
    "6.15.20-251021-apache",  # PATCH for question answers is broken
)
PATTERN_VERSION = re.compile(r"(\d+\.\d+\.\d+)-\d{6}-apache")
PATTERN_5x = re.compile(r"5\.\d+.\d+-\d{6}-apache")
PATTERN_6x = re.compile(r"6\.\d+.\d+-\d{6}-apache")

requests_cache.install_cache("docker_tags")


def _version_parts(tag: str) -> tuple[int, int, int]:
    """Extract version parts from tag.

    Args:
        tag: A tag.

    Returns:
        A tuple of integers representing the version parts.
    """
    return (
        tuple(int(part) for part in match.group(1).split("."))
        if (match := PATTERN_VERSION.match(tag))
        else (999,)
    )


def _extract_version(tag: dict) -> tuple[int, ...]:
    """Extract version from tag.

    Args:
        tag: A tag.

    Returns:
        A tuple of integers representing the version.
    """
    return _version_parts(tag["name"])


def get_tags() -> Generator[dict, None, None]:
    """Get all tags from the Docker Hub.

    Yields:
        Tag data.
    """
    url = (
        "https://hub.docker.com/v2/namespaces/martialblog/repositories/limesurvey/tags"
    )
    while True:
        data = requests.get(url, timeout=30).json()
        yield from data["results"]

        url = data.get("next")
        if not url:
            break


def filter_tags(
    tags: Iterable[dict],
    *,
    max_tags: int = 3,
) -> Generator[str, None, None]:
    """Filter tags.

    Args:
        tags: An iterable of tags.
        max_tags: Maximum number of tags to yield.

    Yields:
        Tag names.
    """
    count_6 = 0
    for tag in tags:
        name = tag["name"]

        if name in SKIP_TAGS:
            continue

        if name in {"6-apache", "5-apache"}:
            yield name

        if re.match(PATTERN_6x, name) and count_6 < max_tags:
            yield name
            count_6 += 1

    yield from DEFAULT_TAGS


def main() -> None:
    """Print tags."""

    class ParserNamespace(argparse.Namespace):
        """Namespace for CLI arguments."""

        max_tags: int
        tags_file: pathlib.Path
        markdown_block_file: pathlib.Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-tags",
        type=int,
        default=3,
        help="Maximum tags to present for each version.",
    )
    parser.add_argument(
        "--tags-file",
        type=pathlib.Path,
        default=pathlib.Path(".github/workflows/resources/tags.json"),
        help="Path to the target tags file.",
    )
    parser.add_argument(
        "--markdown-block-file",
        type=pathlib.Path,
        default=pathlib.Path("docs/_partial/tags.md"),
        help="Path to the target markdown block file.",
    )
    args = parser.parse_args(namespace=ParserNamespace)

    tags = list(
        filter_tags(
            sorted(get_tags(), key=_extract_version, reverse=True),
            max_tags=args.max_tags,
        )
    )

    with args.tags_file.open("w") as file:
        json.dump(tags, file, indent=2)
        file.write("\n")

    with args.markdown_block_file.open("w") as file:
        # 1. Filter out '6-apache' and '5-apache' tags
        # 2. Sort tags by version
        # 3. Convert '6.10.5-250217-apache' to '- {ls_tag}`6.10.0+250
        tags = [
            tag
            for tag in sorted(tags, key=_version_parts, reverse=True)
            if tag not in {"6-apache", "5-apache"}
        ]

        for tag in tags:
            # Convert '6.10.5-250217-apache' to '- {ls_tag}`6.10.0+250106'
            version, date, _ = tag.split("-")
            file.write(f"- {{ls_tag}}`{version}+{date}`\n")


if __name__ == "__main__":
    main()
