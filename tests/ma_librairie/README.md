[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://dev.to/frostming/a-review-pipenv-vs-poetry-vs-pdm-39b4)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Python](https://img.shields.io/badge/python-3.8-green)
![Doc](build/htmldoc/doc_badge.svg)
![Coverage](build/htmldoc/cov_badge.svg)

# Quick look

Tetser mon bulid backend

# Build the doc

Just run:

    git-changelog --output CHANGELOG.md --in-place --version-regex '<a href="[^"]+">(?P<version>[^<]+)' --marker-line '<!-- new entries will be injected here -->'
    pdm doc

This will create the doc in build/htmldoc

A few guidelines for updating the doc
https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
