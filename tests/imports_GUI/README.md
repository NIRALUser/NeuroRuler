# README

The tests in this directory aren't run by `tox` (see `tox.ini`).

This is because `tox` is run in CI, and we don't want to install GUI dependencies in CI, which would cause an error.

This does mean that if you run `tox` locally, you won't see the results of these tests. But realistically, no one is going to run `tox` locally. Just run `pytest`, which will discover these tests.
