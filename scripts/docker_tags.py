"""Get all tags from the Docker Hub."""  # noqa: INP001

from __future__ import annotations

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
    """Extract version from tag."""
    name = tag["name"]
    return (
        tuple(int(part) for part in match.group(1).split("."))
        if (match := PATTERN_VERSION.match(name))
        else (999,)
    )


def get_tags() -> t.Generator[dict, None, None]:
    """Get all tags from the Docker Hub."""
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
    """Sort tags."""
    return sorted(tags, key=_extract_version, reverse=True)


def filter_tags(tags: t.Iterable[dict]) -> t.Generator[str, None, None]:
    """Filter tags."""
    count_5 = 0
    count_6 = 0
    for tag in tags:
        name = tag["name"]
        if name in {"6-apache", "5-apache"}:
            yield name
        if re.match(PATTERN_5x, name) and count_5 < 3:  # noqa: PLR2004
            yield name
            count_5 += 1
        if re.match(PATTERN_6x, name) and count_6 < 3:  # noqa: PLR2004
            yield name
            count_6 += 1


def main() -> None:
    """Print tags."""
    tags = filter_tags(sort_tags(get_tags()))
    print(json.dumps(list(tags)))  # noqa: T201


if __name__ == "__main__":
    main()
