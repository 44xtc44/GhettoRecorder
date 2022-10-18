""" console module,
imports ghetto_recorder and calls ghetto_recorder.terminal_main()
entry point in pyproject.toml
"""
import sys
from os import path
import ghetto_recorder

this_dir = path.abspath(path.join(path.dirname(__file__)))
sys.path.append(this_dir)
print(this_dir)


def main():
    # command line version; write:python ghetto_recorder.py
    ghetto_recorder.terminal_main()
    pass


if __name__ == '__main__':
    main()
