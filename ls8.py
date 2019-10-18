#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

argument = sys.argv[1]

cpu = CPU()

cpu.load(file_path=argument)
cpu.run()
