"""Print markdown table with integration results."""  # noqa: INP001

from __future__ import annotations

import json
import re
from pathlib import Path

from tabulate import tabulate

FILENAME = ".limesurvey-docker-tags.json"
ALT_TEMPLATE = "Status of {git_tag} integration tests, {database}"
GIST_TEMPLATE = (
    "https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com"
    "%2Fedgarrmondragon%2Fcitric%2Fci%2Fbadges-in-repo%2Fassets%2Fbadge%2F"
    "badge-integration-{python}-{docker_tag}-{database}.json"
)


def image(
    git_tag: str,
    database: str,
    python: str,
    docker_tag: str,
) -> str:
    """Return image."""
    alt = ALT_TEMPLATE.format(git_tag=git_tag, database=database)
    url = GIST_TEMPLATE.format(
        python=python,
        docker_tag=docker_tag,
        database=database,
    )
    return f"![{alt}]({url})"


def label(docker_tag: str) -> str:
    """Get label from Docker tag name."""
    if match := re.match(r"(\d+\.\d+.\d+-\d{6})-apache", docker_tag):
        return f"{match[1].replace('-', '+')}"
    if match := re.match(r"(\d+)-apache", docker_tag):
        return f"Latest {match[1]}"

    message = f"Invalid docker tag: {docker_tag}"
    raise ValueError(message)


def main() -> None:
    """Print markdown table with integration results."""
    tags = json.loads(Path(FILENAME).read_text())

    ls_6_tags = [
        ("Latest 6", "PostgreSQL", image("6+", "postgres", "3.11", "6-apache")),
        ("Latest 6", "MySQL", image("6+", "mysql", "3.11", "6-apache")),
    ]
    ls_6_tags.extend(
        (
            label(tag),
            "PostgreSQL",
            image(label(tag), "postgres", "3.11", tag.replace("+", "-")),
        )
        for tag in tags
        if tag.startswith("6") and tag != "6-apache"
    )

    ls_5_tags = [
        ("Latest 5", "PostgreSQL", image("5+", "postgres", "3.11", "5-apache")),
    ]
    ls_5_tags.extend(
        (
            label(tag),
            "PostgreSQL",
            image(label(tag), "postgres", "3.11", tag.replace("+", "-")),
        )
        for tag in tags
        if tag.startswith("5") and tag != "5-apache"
    )

    branches = [
        (
            "`master` branch",
            "PostgreSQL",
            image("master branch", "postgres", "3.11", "refs-heads-master"),
        ),
        (
            "`develop` branch",
            "PostgreSQL",
            image("develop branch", "postgres", "3.11", "refs-heads-develop"),
        ),
        (
            "`5.x` branch",
            "PostgreSQL",
            image("5.x branch", "postgres", "3.11", "refs-heads-5.x"),
        ),
    ]

    print(  # noqa: T201
        tabulate(
            [*ls_6_tags, *ls_5_tags, *branches],
            headers=("LimeSurvey version", "Database", "Status"),
            tablefmt="github",
        ),
    )


if __name__ == "__main__":
    main()
