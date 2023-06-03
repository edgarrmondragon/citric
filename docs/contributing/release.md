# Publish a new version to PyPI

1. Trigger the [Generate release Pull Request][gen-release-pr] workflow.

   The [GitHub CLI](https://github.com/cli/cli/) is very convenient for this:

   ```console
   $ gh workflow run gen-release-pr.yml
   ✓ Created workflow_dispatch event for gen-release-pr.yml at main

   To see runs for this workflow, try: gh run list --workflow=gen-release-pr.yml
   ```

   ````{tip}
   You can specify the bump type, prerelease and metadata with the `-f` option:

   ```shell
   gh workflow run gen-release-pr.yml -f next-version=minor -f prerelease=b1
   ```
   ````

1. Validate the release notes and publish the generated [draft release](https://github.com/edgarrmondragon/citric/releases).

[gen-release-pr]: https://github.com/edgarrmondragon/citric/actions/workflows/gen-release-pr.yml
