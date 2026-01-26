# Setting up your environment

## Get Started

Ready to contribute? Here's how to set up `citric` for local development.

1. Fork the citric repo on GitHub.

1. Clone your fork locally:

   ```shell
   git clone https://github.com/edgarrmondragon/citric.git
   cd citric
   ```

1. Install [`uv`][uv].

1. Check the available [Nox] sessions:

   ```shell
   ./noxfile.py -l
   ```

1. Create a branch for local development:

   ```shell
   git switch -c name-of-your-bugfix-or-feature
   ```

   Now you can make your changes locally.

1. To check that your changes pass the project style checks, use [`prek`][prek]:

   ```shell
   prek install
   prek run --all-files
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
[prek]: https://github.com/j178/prek
[uv]: https://docs.astral.sh/uv/getting-started/installation/
