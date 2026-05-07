#!/usr/bin/env python3

"""
BulkPokeScan - Pokémon TCG Code Scanner and Manager

This script launches the BulkPokeScan application, which allows users to rapidly scan
Pokémon TCG QR code redemption cards with their webcam and efficiently manage
large quantities of codes for redemption.
"""

import sys
import os

# Add the project directory to the Python path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

# Import directly from the src module
from src.main import main

if __name__ == "__main__":
    main() 