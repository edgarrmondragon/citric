# Publish a new version to PyPI

1. Trigger the [Generate release Pull Request][gen-release-pr] workflow with the
desired package version.

   The [GitHub CLI](https://github.com/cli/cli/) is very convenient for this:

   ```console
   $ gh workflow run
   ? Select a workflow Generate release Pull Request (gen-release-pr.yml)
   ? changie-version 1.7.0
   ? next-version patch
   ✓ Created workflow_dispatch event for gen-release-pr.yml at main
   ```

1. Create a [release](https://github.com/edgarrmondragon/citric/releases/new).

[gen-release-pr]: https://github.com/edgarrmondragon/citric/actions/workflows/gen-release-pr.yml
