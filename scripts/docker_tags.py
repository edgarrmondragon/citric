# /// script
# dependencies = ["requests", "requests-cache"]
# requires-python = ">=3.9"
# ///

"""Get all tags from the Docker Hub."""

from __future__ import annotations

import argparse
import json
import re
import typing as t

import requests
import requests_cache

PATTERN_VERSION = re.compile(r"(\d+\.\d+\.\d+)-\d{6}-apache")
PATTERN_5x = re.compile(r"5\.\d+.\d+-\d{6}-apache")
PATTERN_6x = re.compile(r"6\.\d+.\d+-\d{6}-apache")

requests_cache.install_cache("docker_tags")


def _extract_version(tag: dict) -> tuple[int, ...]:
    """Extract version from tag.

    Args:
        tag: A tag.

    Returns:
        A tuple of integers representing the version.
    """
    name = tag["name"]
    return (
        tuple(int(part) for part in match.group(1).split("."))
        if (match := PATTERN_VERSION.match(name))
        else (999,)
    )


def get_tags() -> t.Generator[dict, None, None]:
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


def sort_tags(tags: t.Iterable[dict]) -> list[dict]:
    """Sort tags.

    Args:
        tags: An iterable of tags.

    Returns:
        A list of tags sorted by version
    """
    return sorted(tags, key=_extract_version, reverse=True)


def filter_tags(
    tags: t.Iterable[dict],
    *,
    max_tags: int = 3,
) -> t.Generator[str, None, None]:
    """Filter tags.

    Args:
        tags: An iterable of tags.
        max_tags: Maximum number of tags to yield.

    Yields:
        Tag names.
    """
    count_5 = 0
    count_6 = 0
    for tag in tags:
        name = tag["name"]

        if name in {"6-apache", "5-apache"}:
            yield name

        if re.match(PATTERN_5x, name) and count_5 < max_tags:
            yield name
            count_5 += 1

        if re.match(PATTERN_6x, name) and count_6 < max_tags:
            yield name
            count_6 += 1


def main() -> None:
    """Print tags."""

    class ParserNamespace(argparse.Namespace):
        """Namespace for CLI arguments."""

        max_tags: int

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-tags",
        type=int,
        default=3,
        help="Maximum tags to present for each version.",
    )
    args = parser.parse_args(namespace=ParserNamespace)

    tags = filter_tags(sort_tags(get_tags()), max_tags=args.max_tags)
    print(json.dumps(list(tags)))  # noqa: T201


if __name__ == "__main__":
    main()
