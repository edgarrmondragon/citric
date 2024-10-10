# Update GitHub Actions pins

There are a few ways to update the GitHub Actions pins.

## Run workflow in GitHub

Go to the [Actions tab](https://github.com/edgarrmondragon/citric/actions/workflows/gha-update.yml) and click on the `Run workflow` dropdown.

## Run workflow locally

1. Install the [GitHub CLI](https://cli.github.com/).

1. Run the following command:

   ```bash
   gh workflow run gha-update.yml
   ```

## Run the `gha-update` tool locally

1. Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/).

1. Run the following command:

   ```bash
   uvx gha-update
   ```
