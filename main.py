#! /usr/bin/env python

import datoszs.commands.prepare_cc_data as prepare_cc_data
from datoszs.db import global_connection


if __name__ == "__main__":
    with global_connection():
        prepare_cc_data.execute()
