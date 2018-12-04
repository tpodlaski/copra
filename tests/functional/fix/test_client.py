#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Functional tests for `copra.fixt.Client` class.
"""

import os.path
import sys

from asynctest import TestCase

from copra.fix import Client, SANDBOX_URL

if not os.path.isfile(os.path.join(os.path.dirname(__file__), '.env')):
    print("\n** .env file not found. **\n")
    sys.exit()

from dotenv import load_dotenv
load_dotenv()

KEY = os.getenv('KEY')
SECRET = os.getenv('SECRET')
PASSPHRASE = os.getenv('PASSPHRASE')

class TestFix(TestCase):
    """Tests for copra.fix.Client"""
    
    