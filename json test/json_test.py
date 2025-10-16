# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 08:23:23 2024

@author: barna
"""

import json

data = {
  "fruits": ["apple", "banana", "cherry"],
  "colors": ["red", "green", "blue"],
  "cities": ["New York", "London", "Paris"]
}


with open("data.json", 'w') as file:
    data = json.load(file)

