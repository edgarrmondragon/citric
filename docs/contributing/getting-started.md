# Getting Started

Contributions are welcome, and they are greatly appreciated! Every little bit helps,
and credit will always be given.

You can contribute in many ways.

## Types of Contributions

### Report bugs or request features

Report bugs and request new features in the repo [issue tracker][new-issue].
The issueforms will guide to include all necessary information, like package version,
Python version, operating system, and so on.

### Fix bugs or implement features

Look through the [GitHub issues][issues] for bugs and features. Anything tagged with
["bug" and "help wanted"][bug-help-wanted] is open to whoever wants to implement it.
Anything tagged with ["enhancement" and "help wanted"][feature-help-wanted] is open
to whoever wants to implement it.

### Write Documentation

Citric could always use more documentation, whether as part of the
official Citric docs, in docstrings, or even on the web in blog posts,
articles, and such.

If you're updating the Sphinx docs, you might want to check out [the docs guide][docs].


### Changelog

If your change is noteworthy, there needs to be a changelog entry in [`CHANGELOG.md`](https://github.com/edgarrmondragon/citric/blob/main/CHANGELOG.md), so our users can learn about it!

- The changelog follows the [*Keep a Changelog*](https://keepachangelog.com/en/1.0.0/) standard.
  Please add the best-fitting section if it's missing for the current release.
  We use the following order: `Security`, `Removed`, `Deprecated`, `Added`, `Changed`, `Fixed`, `Documentation`.
- Please use [semantic newlines] in the changelog.
- Add a link to your pull request.
  You probably have to open it first to know the number.
- Wrap symbols like modules, functions, or classes into backticks so they are rendered in a `monospace font`.
- Wrap arguments into asterisks:
  `Added new argument *an_argument*.`
- If you mention methods or other callables, add parentheses at the end of their names:
  `citric.Client.method()`.
  This makes the changelog a lot more readable.
- Prefer simple past tense or constructions with "now".
  For example:

  * Added `citric.Client.get_db_version()`.


[new-issue]: https://github.com/edgarrmondragon/citric/issues/new/choose
[issues]: https://github.com/edgarrmondragon/citric/issues
[bug-help-wanted]: https://github.com/edgarrmondragon/citric/issues?q=is%3Aopen+is%3Aissue+label%3Abug+label%3A%22help+wanted%22
[feature-help-wanted]: https://github.com/edgarrmondragon/citric/issues?q=is%3Aopen+is%3Aissue+label%3Aenhancement+label%3A%22help+wanted%22
[docs]: /contributing/docs
[semantic newlines]: https://rhodesmill.org/brandon/2012/one-sentence-per-line/
