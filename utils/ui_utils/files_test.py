# -*- coding: utf-8 -*-
"""
Created on Sun Oct 12 19:58:20 2025

@author: barna
"""

from pathlib import Path

current_dir = Path(__file__).parent
target_dir = current_dir / 'ui_elements'

#ui_elements = list(target_dir.glob('*.png'))



image_dict = {path.stem: path for path in target_dir.glob('*.png')}


print(image_dict)