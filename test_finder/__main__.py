import os
import sys
from typing import List

from tree_sitter import Language
from tree_sitter import Parser
from tree_sitter import Tree
from tree_sitter import TreeCursor
from tree_sitter import Node


def main(args: List[str]) -> int:
    args = args[1:]
    if len(args) != 2:
        print_usage("Improper number of arguments")
        return 1

    path = args[0]
    try:
        with open(path, "r") as f:
            contents = bytes(f.read(), "utf8")
    except FileNotFoundError:
        print_usage("File does not exist")
        return 1

    try:
        row = int(args[1])
    except ValueError:
        print_usage("Row must be an integer")
        return 1

    # rows in most editors are 1-indexed,
    # but treesitter is 0 indexed.
    # so we just subtract 1 :)
    row -= 1

    language = build_py_language()
    parser = Parser()
    parser.set_language(language)

    tree = parser.parse(contents)
    node = most_specific_node(tree.root_node, row)

    namespace = calculate_test_namespace(contents, node)
    if namespace.strip() == "":
        print(f"No test declaration at {path}:{row + 1}")
        return 1
    else:
        print(f"{path}::{namespace}")
    return 0


def build_py_language() -> Language:
    exec_root = os.path.dirname(__file__)
    python_so = f"{exec_root}/build/python.so"
    if not os.path.exists(python_so):
        Language.build_library(python_so, ["tree-sitter-python"])
    return Language(python_so, "python")


def most_specific_node(node: Node, row: int) -> Node:
    point = (row, 0)
    assert (
        node.start_point <= point <= node.end_point
    ), f"row must be within bounds, not {node.start_point} </= {point} </= {node.end_point}"

    for child in node.children:
        if child.start_point <= point <= child.end_point:
            return most_specific_node(child, row)
    return node


def calculate_test_namespace(contents: bytes, node: Node) -> str:
    namespaces = []
    relevant_types = {"class_definition", "function_definition"}
    while node.parent is not None:
        if node.type in relevant_types:
            identifier = node.child_by_field_name("name")
            namespaces.append(
                contents[identifier.start_byte : identifier.end_byte].decode("utf8")
            )
        node = node.parent
    return "::".join(reversed(namespaces))


def print_usage(error: str = ""):
    if error:
        print(error)
    print("Usage:\n    test-finder <path/to/file> <row>")


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as e:
        print(f"Encountered error: {str(e)}")
        sys.exit(1)