#!/usr/bin/env python3
"""
generate a test offer and print out the invitation link.
"""


import os
import sys

TOP_STORMX_DIR = os.path.join(os.path.dirname(sys.argv[0]), '..', 'Stormx')
sys.path.insert(0, TOP_STORMX_DIR)

from StormxApp.tests.utilities import create_test_offer

def main():
    create_test_offer(open_in_browser=False, enable_email=False)

if __name__ == '__main__':
    main()
