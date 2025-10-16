# -*- coding: utf-8 -*-
"""
Created on Sun Oct 12 19:58:20 2025

@author: barna
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Takes the current directory and target directory and returns dictionary
# of stem name to path
def get_ui_elements():
    target_dir = PROJECT_ROOT / 'utils' / 'ui_utils' /'ui_elements'
    
    stem_to_path = {
        path.stem: path.resolve() for path in target_dir.glob('*.png')
        }
    
    
    return stem_to_path