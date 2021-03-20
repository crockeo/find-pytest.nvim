# find-pytest.nvim

You know that feeling when you're working on a large Python project
and you don't really want to spend 40 minutes waiting for a bloated unit test suite to run.
So you painstakingly write out the `full/path/to.py::the_test_you_want_to_run`?

Well write no more! `find-pytest.nvim` is here to save you!
`find-pytest.nvim` provides two features for your enjoyment:

1. `FindPytest` is a function that returns the fully namespaced path to a test
   which you can pass right into `pytest`.
1. `YankPytest` copies the result of `FindPytest` right to your clipboard
   so you can swap to your other window.

## Installation

Requires:
- python3
- `pip install pynvim tree_sitter`
  - **TODO**: prompt the user to `pip install -r requirements.txt` when we run :)
