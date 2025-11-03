#!/usr/bin/env python3
"""
simple_constraint_cells.py
==========================

Simple script that uses the existing _discover_constraint_cells method
from the multi-level optimizer to print constraint cells.

Usage:
    python simple_constraint_cells.py
"""

import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from rtf_core.multi_level_optimizer import RTFMultiLevelAlgorithm


def print_constraint_cells(target_cell_info, dataset='adult'):
    """Print constraint cells using the existing multi-level optimizer."""
    
    print("=" * 60)
    print("CONSTRAINT CELLS USING MULTI-LEVEL OPTIMIZER")
    print("=" * 60)
    
    try:
        # Create the algorithm
        algorithm = RTFMultiLevelAlgorithm(target_cell_info, dataset, 0.8)
        
        # Run the algorithm to trigger initialization and constraint discovery
        algorithm.run_complete_algorithm()
        
        # Get the constraint cells from the init_manager
        constraint_cells = algorithm.init_manager.constraint_cells
        
        print(f"Target: {target_cell_info}")
        print(f"Constraint cells found: {len(constraint_cells)}")
        
        for i, cell in enumerate(constraint_cells, 1):
            print(f"{i}. {cell.attribute.col} = {cell.value}")
            
    except Exception as e:
        print(f"Error: {e}")
        print("This is normal if MySQL is not running.")


if __name__ == '__main__':
    # Test with different targets
    targets = [
        {'key': 2, 'attribute': 'education'},
        {'key': 5, 'attribute': 'age'},
        {'key': 10, 'attribute': 'occupation'}
    ]
    
    for target in targets:
        print_constraint_cells(target)
        print()
