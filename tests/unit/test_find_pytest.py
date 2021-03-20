from unittest.mock import mock_open

import pytest

from rplugin.python3 import find_pytest


FILE_CONTENTS = """\
import pytest

class TestThisGroupOfThings:
    def test_function(self):
        # this isn't a tautology i promise
        assert 1 == 1

def test_bare_function():
    assert ",".join([1, 2, 3]) == "1,2,3"
"""


@pytest.mark.parametrize(
    "row, expected_namespace",
    [
        (5, "TestThisGroupOfThings::test_function"),
        (8, "test_bare_function"),
    ],
)
def test_get_pytest_selector(mocker, row, expected_namespace):
    mocker.patch.object(
        find_pytest,
        "open",
        mock_open(read_data=FILE_CONTENTS),
    )
    pytest_selector = find_pytest.get_pytest_selector("asdf.txt", row)
    assert pytest_selector == f"asdf.txt::{expected_namespace}"
