""" console module,
imports ghetto_recorder and calls ghetto_recorder.terminal_main()
entry point in pyproject.toml
"""
import sys
from os import path

# load standard path set
this_dir = path.abspath(path.dirname(__file__))
api_dir = path.abspath(path.join(path.dirname(__file__), 'api'))
lib_dir = path.abspath(path.join(path.dirname(__file__), 'lib'))
sys.path.append(path.abspath(this_dir))
sys.path.append(path.abspath(api_dir))
sys.path.append(path.abspath(lib_dir))
print(sys.path)
import ghetto_recorder

def main():
    # command line version; write:python ghetto_recorder.py
    ghetto_recorder.terminal_main()


if __name__ == '__main__':
    main()
