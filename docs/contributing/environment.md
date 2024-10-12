# Setting up your environment

## Get Started

Ready to contribute? Here's how to set up `citric` for local development.

1. Fork the citric repo on GitHub.

1. Clone your fork locally:

   ```shell
   git clone https://github.com/edgarrmondragon/citric.git
   cd citric
   ```

1. Optional: install [`uv`][uv].

1. Install [`nox`][nox] (used for automation):

   ```shell
   pipx install 'nox[uv]'
   nox -l
   ```

   Or use `uv` to install `nox`:

   ```shell
   uv tool install nox
   ```

1. Create a branch for local development:

   ```shell
   git checkout -b name-of-your-bugfix-or-feature
   ```

   Now you can make your changes locally.

1. To check that your changes pass the project style checks, use [`pre-commit`][pre-commit]:

   ```shell
   pre-commit install
   pre-commit run --all-files
   ```

1. Commit your changes and push your branch to GitHub:

   ```shell
   git add .
   git commit -m "Your detailed description of your changes."
   git push origin name-of-your-bugfix-or-feature
   ```

1. Submit a pull request through the GitHub website.

1. (Optional) Add a changelog entry using [`changie`][changie]. You'll need to install the Changie CLI in order to add a changelog entry:

   ```shell
   changie new
   ```

[changie]: https://changie.dev/
[nox]: https://nox.thea.codes/en/stable/
[pre-commit]: https://pre-commit.com/
[uv]: https://docs.astral.sh/uv/
