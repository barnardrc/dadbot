# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 08:23:23 2024

@author: barna
"""

import json
import os
from utils.logger import logger as log

def find_file(file):
    for r,d,f in os.walk(r"C:\\"):
        for files in f:
            if files == file:
                return os.path.join(r, files)

def path_check(file_path: str = 'data.json') -> None:

    if not os.path.exists(file_path):
        initial_data = {}
        with open(file_path, "w") as file:
            json.dump(initial_data, file, indent=4)
        log.debug(f"{file_path} created successfully!")
        
    else:
        log.debug(f"{file_path} already exists.")
        
def item_check(item: str) -> bool:
    try:
        with open("data.json", 'r') as file:
            data = json.load(file)
    
        if item in data:
            return True
        
        elif item not in data:
            return False
    
    except Exception as e:
        log.error(f"item_check: {e}", exc_info=True)

def get_item_data(item: str) -> tuple[list, int]:
    with open('data.json', 'r') as file:
        data = json.load(file)
    
    return (data[item]['dimensions'], data[item]['is_gold_storage'], data[item]['is_stackable'], data[item]['max_stack'])
    
def item_write(item: str, dimensions: tuple, is_gold_storage: bool,
               is_stackable: bool, max_stack: int) -> None:
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
            
        if item not in data:
            data[item] = {}
        
        data[item]['dimensions'] = dimensions
        data[item]['is_gold_storage'] = is_gold_storage
        data[item]['is_stackable'] = is_stackable
        data[item]['max_stack'] = max_stack
        
        with open("data.json", 'w') as file:
            json.dump(data, file, indent = 4)
    
        log.debug("Data entry updated successfully!")
        
    except KeyError as e:
        log.error(f"KeyError in item_write: {e}", exc_info=True)
        
    except FileNotFoundError:
        log.error("data.json file not found!")
        
    except json.JSONDecodeError:
        log.error("Invalid JSON format in data.json!")
        
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}", exc_info=True)
        