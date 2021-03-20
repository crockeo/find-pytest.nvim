import os
from typing import cast

import pynvim
from tree_sitter import Language
from tree_sitter import Parser
from tree_sitter import Tree
from tree_sitter import TreeCursor
from tree_sitter import Node


@pynvim.plugin
class FindPytest:
    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim

    @pynvim.command("YankPytest")
    def yank_pytest(self):
        try:
            pytest_selector = self.find_pytest()
            self.nvim.command(f'let @+ = "{pytest_selector}"')
            self.nvim.command(f"echo \"Yanked '{pytest_selector}' to clipboard\"")
        except Exception as e:
            message = f"Failed to yank test name: {str(e)}"
            self.nvim.command(f'echo "{message}"')

    @pynvim.command("FindPytest", sync=True)
    def find_pytest(self) -> str:
        file_path = cast(str, self.nvim.call("expand", "%@"))
        # we subtract one becuase vim rows are 1-indexed
        # but treesitter rows are 0-indexed
        row = cast(int, self.nvim.call("line", ".")) - 1
        return get_pytest_selector(file_path, row)


def get_pytest_selector(file_path: str, row: int) -> str:
    with open(file_path, "r") as f:
        contents = bytes(f.read(), "utf8")

    parser = Parser()
    parser.set_language(py_language())
    node = most_specific_node(parser.parse(contents).root_node, row)

    namespace = calculate_pytest_selector(contents, node)
    return f"{file_path}::{namespace}"


def py_language() -> Language:
    exec_root = os.path.dirname(__file__)
    python_so = f"{exec_root}/build/python.so"
    if not os.path.exists(python_so):
        Language.build_library(python_so, ["tree-sitter-python"])
    return Language(python_so, "python")


def most_specific_node(node: Node, row: int) -> Node:
    point = (row, 0)
    assert (
        node.start_point <= point <= node.end_point
    ), f"failed to find python test parse node"

    for child in node.children:
        if child.start_point <= point <= child.end_point:
            return most_specific_node(child, row)
    return node


def calculate_pytest_selector(contents: bytes, node: Node) -> str:
    namespaces = []
    relevant_types = {"class_definition", "function_definition"}
    while node.parent is not None:
        if node.type in relevant_types:
            identifier = node.child_by_field_name("name")
            namespaces.append(
                contents[identifier.start_byte : identifier.end_byte].decode("utf8")
            )
        node = node.parent
    if len(namespaces) == 0:
        raise Exception("node not within class/function definition")
    return "::".join(reversed(namespaces))
