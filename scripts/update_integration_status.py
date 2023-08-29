"""Update markdown file with content from another file."""  # noqa: INP001

from __future__ import annotations

from pathlib import Path


def update_markdown_with_content(
    markdown_path: str,
    content_path: str,
    start_marker: str = "<!-- start integration status -->\n",
    end_marker: str = "<!-- end integration status -->\n",
) -> None:
    """Update markdown file with content from another file."""
    # Read existing markdown content
    markdown_content = Path(markdown_path).read_text()

    # Read content to be included
    content_to_include = Path(content_path).read_text()

    # Find the positions of the start and end markers
    start_pos = markdown_content.find(start_marker)
    end_pos = markdown_content.find(end_marker)

    #  Check if the markers are found
    if start_pos != -1 and end_pos != -1:
        # Replace the content between the markers with new content
        updated_markdown_content = (
            markdown_content[: start_pos + len(start_marker)]
            + content_to_include
            + markdown_content[end_pos:]
        )
        print(updated_markdown_content.strip())  # noqa: T201


if __name__ == "__main__":
    markdown_file_path = "README.md"
    content_file_path = "status.temp.md"

    update_markdown_with_content(markdown_file_path, content_file_path)
