import os

from tree_sitter import Language
from tree_sitter import Parser
from tree_sitter import Tree
from tree_sitter import TreeCursor
from tree_sitter import Node


def get_test_namespace(file_path: str, row: int) -> str:
    with open(file_path, "r") as f:
        contents = bytes(f.read(), "utf8")

    parser = Parser()
    parser.set_language(py_language())
    node = most_specific_node(parser.parse(contents).root_node, row)

    namespace = calculate_test_namespace(contents, node)
    return f"{file_path}::{namespace}"


def py_language() -> Language:
    exec_root = os.path.dirname(__file__)
    python_so = f"{exec_root}/build/python.so"
    if not os.path.exists(python_so):
        raise FileNotFoundError(
            "could not find python treesitter grammar.\n"
            "was this package built properly?"
        )
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
