#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Functional tests for `copra.fixt.Client` class.
"""

import os.path
import sys

if not os.path.isfile(os.path.join(os.path.dirname(__file__), '.env')):
    print("\n** .env file not found. **\n")
    sys.exit()

from dotenv import load_dotenv
load_dotenv()

