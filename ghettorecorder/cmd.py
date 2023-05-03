""" console module,
imports ghetto_recorder and calls ghetto_recorder.terminal_main()
entry point in pyproject.toml
"""
from ghettorecorder.ghetto_recorder import terminal_main


def main():
    # command line version calls module as main, not as library
    terminal_main()
    pass


if __name__ == '__main__':
    main()
