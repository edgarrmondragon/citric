#!/usr/bin/env -S uv run --script

# Copyright (c) 2026 Edgar Ramírez-Mondragón

# /// script
# dependencies = []
# requires-python = ">=3.11"
# ///

"""Summarize LimeSurvey RemoteControl and REST API changes between two releases."""

from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import re
import urllib.error
import urllib.parse
import urllib.request
from http import HTTPStatus

REPO = "LimeSurvey/LimeSurvey"
RPC_FILE = "application/helpers/remotecontrol/remotecontrol_handle.php"
REST_ROUTES_DIR = "application/config/rest/v1"
API_PATHS = (
    "application/helpers/remotecontrol/",
    "application/config/rest/",
    "application/libraries/Api/",
)
TAGS_FILE = pathlib.Path(".github/tags.json")
MAX_TAG_PAGES = 5

PATTERN_RELEASE = re.compile(r"^(\d+)\.(\d+)\.(\d+)\+(\d{6})$")
PATTERN_DOCKER_TAG = re.compile(r"^(\d+\.\d+\.\d+)-(\d{6})-apache$")
PATTERN_RPC_METHOD = re.compile(r"public function (\w+)\s*\(([^)]*)\)")
PATTERN_REST_ROUTE = re.compile(r"\$rest\['([^']+)'\]\s*=\s*\[")
PATTERN_REST_VERB = re.compile(
    r"^\s*'(GET|POST|PUT|PATCH|DELETE)'\s*=>\s*\[",
    re.MULTILINE,
)
PATTERN_REST_COMMAND = re.compile(r"'commandClass'\s*=>\s*(\w+)::class")

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def _request(url: str) -> bytes:
    """Fetch a URL, using ``GITHUB_TOKEN`` for the GitHub API if available.

    Args:
        url: The URL to fetch.

    Returns:
        The response body.
    """
    headers = {"User-Agent": "citric-limesurvey-api-diff"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)  # ruff: ignore[suspicious-url-open-usage]
    with urllib.request.urlopen(request, timeout=30) as response:  # ruff: ignore[suspicious-url-open-usage]
        return response.read()


def _api(path: str) -> object:
    """Call the GitHub API.

    Args:
        path: API path, relative to the repository.

    Returns:
        The decoded JSON response.
    """
    return json.loads(_request(f"https://api.github.com/repos/{REPO}/{path}"))


def _raw(ref: str, path: str) -> str:
    """Get the contents of a file at a given ref.

    Args:
        ref: A tag or branch.
        path: Path of the file in the repository.

    Returns:
        The file contents.
    """
    quoted_ref = urllib.parse.quote(ref, safe="")
    url = f"https://raw.githubusercontent.com/{REPO}/{quoted_ref}/{path}"
    return _request(url).decode()


def release_tags() -> list[str]:
    """Get upstream release tags, newest first.

    Returns:
        Tags like ``7.8.0+261026``.
    """
    releases: list[str] = []
    for page in range(1, MAX_TAG_PAGES + 1):
        tags = _api(f"tags?per_page=100&page={page}")
        assert isinstance(tags, list)  # ruff: ignore[assert]
        releases += [t["name"] for t in tags if PATTERN_RELEASE.match(t["name"])]
    return sorted(
        releases,
        key=lambda t: tuple(map(int, PATTERN_RELEASE.match(t).groups())),  # type: ignore[union-attr]
        reverse=True,
    )


def resolve_release(ref: str, releases: list[str]) -> str:
    """Resolve a bare version like ``7.5.1`` to its upstream tag.

    Docker image dates don't always match upstream tag dates, so releases are
    matched by version.

    Args:
        ref: A version, tag or branch.
        releases: Known upstream release tags.

    Returns:
        The upstream tag, or ``ref`` unchanged if it isn't a bare version.

    Raises:
        SystemExit: If no upstream release matches the version.
    """
    if not re.fullmatch(r"\d+\.\d+\.\d+", ref):
        return ref
    for tag in releases:
        if tag.startswith(f"{ref}+"):
            return tag
    msg = f"No upstream release found for version {ref}"
    raise SystemExit(msg)


def newest_tested_version() -> str:
    """Get the newest version pinned in the CI matrix.

    Returns:
        A version like ``7.5.1``.
    """
    tags = json.loads(TAGS_FILE.read_text(encoding="utf-8"))
    versions = [m.group(1) for tag in tags if (m := PATTERN_DOCKER_TAG.match(tag))]
    return max(versions, key=lambda v: tuple(map(int, v.split("."))))


def rpc_methods(ref: str) -> dict[str, str]:
    """Parse public RPC methods and their parameters.

    Args:
        ref: A tag or branch.

    Returns:
        A mapping of method name to normalized parameter list.
    """
    source = _raw(ref, RPC_FILE)
    return {
        name: " ".join(params.split())
        for name, params in PATTERN_RPC_METHOD.findall(source)
        if not name.startswith("_")
    }


def _slices(text: str, matches: list[re.Match[str]]) -> list[tuple[re.Match[str], str]]:
    """Pair each match with the text that follows it, up to the next match.

    Args:
        text: The text that was searched.
        matches: Consecutive matches in ``text``.

    Returns:
        Pairs of match and following text.
    """
    ends = [m.start() for m in matches[1:]] + [len(text)]
    return [(m, text[m.end() : end]) for m, end in zip(matches, ends, strict=True)]


def _parse_routes(source: str) -> dict[str, str]:
    """Parse the routes defined in a REST config file.

    Args:
        source: PHP source.

    Returns:
        A mapping of ``"VERB route"`` to command class.
    """
    routes: dict[str, str] = {}
    for route, chunk in _slices(source, list(PATTERN_REST_ROUTE.finditer(source))):
        for verb, body in _slices(chunk, list(PATTERN_REST_VERB.finditer(chunk))):
            command = PATTERN_REST_COMMAND.search(body)
            key = f"{verb.group(1)} /rest/{route.group(1)}"
            routes[key] = command.group(1) if command else "?"
    return routes


def rest_routes(ref: str) -> dict[str, str]:
    """Parse REST routes and the command class handling each.

    Args:
        ref: A tag or branch.

    Returns:
        A mapping of ``"VERB route"`` to command class.

    Raises:
        HTTPError: If the routes can't be listed for a reason other than the REST
            API not existing at ``ref``.
    """
    quoted_ref = urllib.parse.quote(ref, safe="")
    try:
        listing = _api(f"contents/{REST_ROUTES_DIR}?ref={quoted_ref}")
    except urllib.error.HTTPError as e:
        if e.code == HTTPStatus.NOT_FOUND:  # REST API doesn't exist at this ref
            return {}
        raise
    assert isinstance(listing, list)  # ruff: ignore[assert]
    routes: dict[str, str] = {}
    for entry in listing:
        if entry["name"].endswith(".php"):
            routes |= _parse_routes(_raw(ref, entry["path"]))
    return routes


def changed_files(base: str, target: str) -> list[tuple[str, str]]:
    """List changed API files between two refs.

    Args:
        base: Base ref.
        target: Target ref.

    Returns:
        Pairs of file status and path, limited to API-related paths.
    """
    spec = urllib.parse.quote(f"{base}...{target}", safe=".")
    result = _api(f"compare/{spec}")
    assert isinstance(result, dict)  # ruff: ignore[assert]
    return [
        (f["status"], f["filename"])
        for f in result["files"]
        if f["filename"].startswith(API_PATHS)
    ]


def _section(
    title: str,
    old: dict[str, str],
    new: dict[str, str],
    *,
    show: str,
) -> list[str]:
    """Render a Markdown section describing the differences between two maps.

    Args:
        title: Section heading.
        old: Items at the base ref.
        new: Items at the target ref.
        show: What the values are, for the ``changed`` label.

    Returns:
        Lines of Markdown.
    """
    lines = [f"## {title}", ""]
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(k for k in set(old) & set(new) if old[k] != new[k])
    lines += [f"- **added** `{k}` {new[k]}".rstrip() for k in added]
    lines += [f"- **removed** `{k}` {old[k]}".rstrip() for k in removed]
    lines += [f"- **{show} changed** `{k}`: {old[k]} → {new[k]}" for k in changed]
    if not (added or removed or changed):
        lines.append("No changes.")
    lines.append("")
    return lines


def render(base: str, target: str) -> str:
    """Build the Markdown report.

    Args:
        base: Base ref.
        target: Target ref.

    Returns:
        A Markdown report.
    """
    old_rpc, new_rpc = rpc_methods(base), rpc_methods(target)
    old_rest, new_rest = rest_routes(base), rest_routes(target)
    files = changed_files(base, target)

    lines = [f"# LimeSurvey API changes: `{base}` → `{target}`", ""]
    lines += _section(
        "RemoteControl (RPC) methods",
        {k: f"`({v})`" for k, v in old_rpc.items()},
        {k: f"`({v})`" for k, v in new_rpc.items()},
        show="signature",
    )
    lines += _section(
        "REST routes",
        {k: f"(`{v}`)" for k, v in old_rest.items()},
        {k: f"(`{v}`)" for k, v in new_rest.items()},
        show="handler",
    )
    lines += [
        "## Changed API files",
        "",
        (
            "Response fields live in `Transformer/Output/` and `SchemaFactory/`; "
            "read these diffs to find TypedDict changes."
        ),
        "",
        *([f"- {status}: `{path}`" for status, path in files] or ["None."]),
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    """Print the report.

    Raises:
        SystemExit: If a GitHub request fails.
    """

    class ParserNamespace(argparse.Namespace):
        """Namespace for CLI arguments."""

        base: str | None
        target: str | None

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        help=(
            "Release version or tag to compare from, like '7.5.1'. Defaults to the "
            f"newest version pinned in {TAGS_FILE}."
        ),
    )
    parser.add_argument(
        "--target",
        help=(
            "Release version, tag or branch to compare to. Defaults to the newest "
            "release."
        ),
    )
    args = parser.parse_args(namespace=ParserNamespace)

    releases = release_tags()
    base = resolve_release(args.base or newest_tested_version(), releases)
    target = resolve_release(args.target or releases[0], releases)
    logger.info("Comparing %s to %s", base, target)

    try:
        print(render(base, target))  # ruff: ignore[print]
    except urllib.error.HTTPError as e:
        logger.error("GitHub request failed: %s %s (%s)", e.code, e.reason, e.url)  # ruff: ignore[error-instead-of-exception]
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
