from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_ext import build_ext
from tree_sitter import Language


class GrammarBuildExt(build_ext):
    def run(self):
        Language.build_library("test_finder/build/python.so", ["tree-sitter-python"])
        super().run()


setup(
    name="test_finder",
    version="0.0.1",
    cmdclass={"build_ext": GrammarBuildExt},
    author="Cerek Hillen",
    author_email="cerekh@gmail.com",
    url="https://github.com/crockeo/test-finder",
    packages=find_packages(exclude=["tests"]),
    setup_requires=[
        "setuptools",
        "tree_sitter",
        "wheel",
    ],
    install_requires=[
        "tree_sitter",
    ],
)
