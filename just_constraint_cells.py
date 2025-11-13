#!/usr/bin/env python3
"""
just_constraint_cells.py
========================

Just print constraint cells using the existing _discover_constraint_cells method.
"""

import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from rtf_core.initialization_phase import InitializationManager


def print_constraint_cells(target_cell_info, dataset='adult'):
    """Just print the constraint cells."""
    
    print(f"Target: {target_cell_info}")
    
    # Create manager
    manager = InitializationManager(target_cell_info, dataset, 0.8)
    
    # Initialize to discover constraint cells
    manager.initialize()
    
    # Print them
    print(f"Constraint cells: {manager.constraint_cells}")
    for cell in manager.constraint_cells:
        print(f"  {cell.attribute.col} = {cell.value}")


if __name__ == '__main__':
    # Just test one
    print_constraint_cells({'key': 2, 'attribute': 'education'})


