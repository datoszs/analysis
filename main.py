#! /usr/bin/env python
import datoszs.commands
from spiderpig import run_cli


if __name__ == "__main__":
    run_cli(
        command_packages=[datoszs.commands],
    )
