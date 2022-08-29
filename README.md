# PlexiGlass

---

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

---

PlexiGlass is a pure Python library providing common utilities not limited to

- argparse
- logging

It should additionally serve as a good Python project template.

## Installation
```shell
$ pip install poetry

$ poetry config virtualenvs.create false

$ poetry install
```

Optional dependencies can be installed using the extras syntax.
``` shell
$ poetry install -E logging -E synapse
```

A shortcut has been provided to install all optional dependencies.
This is the **recommended** install option for developers working on plexiglass.

```shell
$ poetry install -E all
```

## Development
A test suite is available in the tests directory.

They are found and run with pytest.

```shell
$ py.test

$ poetry run pytest
```

Configuration is found in the `pytest.ini` file.

### Coverage (`pytest-cov`)
The coverage information is retrieved by regex in the GitLab CI (check `.gitlab-ci.yml`).

### Formatting (`pytest-black`)
The code for PlexiGlass is handled by the
[black](https://github.com/python/black) Python code formatter.

``` shell
$ black .
```

### Code Style (`pytest-flake8`)
Code is checked against the [flake8](http://flake8.pycqa.org/en/latest/) tool
as part of the test suite.

Add `# noqa` to the end of lines that should not be linted.

Add `# pragma: no cover` to the end of blocks/statements that should not be covered.

## Library Maintenance

To generally update dependencies that are unbounded,

```
# The lock file will contain any newly updated dependency versions.
# Which we then automatically populate the `setup.py` file with.
$ poetry update

$ dephell convert deps

# DEV: Until https://github.com/dephell/dephell/issues/178 is resolved
#      Remove the `README.rst` and point to `README.md` manually instead.

$ rm -f README.rst
$ sed -i 's#README.rst#README.md#' setup.py
```

Distribution Statement "A" (Approved for Public Release, Distribution
Unlimited).
