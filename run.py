#!/usr/bin/env python3

"""
Runner script for Basic Agent
"""

import os
import sys
from src.main import app

if __name__ == "__main__":
    # Add the current directory to the path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run the app
    app() 