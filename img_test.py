# -*- coding: utf-8 -*-
"""
Created on Wed Oct  8 14:03:29 2025

@author: barna
"""

import pyautogui as pag

# Takes a string of rarity and assigns integer label
def get_rarity(rarity: str):
    
    RARITY_MAPPING = {
        'poor': 1,
        'common': 2,
        'uncommon': 3,
        'rare': 4,
        'epic': 5,
        'legendary': 6,
        'unique': 7
        }
    
    rarity_key = rarity.lower()
    
    val = RARITY_MAPPING.get(rarity_key)
    
    if val is not None:
        return val
    else:
        return 0


def format_item_for_img_loc(item: str, rarity: int = None):
    item = item.lower()
    item = item.replace(' ', '_')
    if rarity is not None:
        item = item + '_' + str(rarity)
    return item + '.png'

def is_sold_check():
    target_area = 'sold_emblem.png'
    file_loc = 'item_images/'
    
    img_loc = file_loc + target_area
    loc = pag.locateCenterOnScreen(img_loc, confidence = 0.9)
    print(loc)

def is_inventory_empty():
    target_area = 'empty_trade_screen.png'
    file_loc = 'item_images/'
    target_img = target_area
    
    img_loc = file_loc + target_img
    print(img_loc)

    loc = pag.locateOnScreen(img_loc, confidence = 0.95)
    print(loc)
    
    
    
    
    
def get_loc_of_item():
    
    item = 'Gold Coin Bag'
    rarity = ''
    item_value = format_item_for_img_loc(item, get_rarity(rarity))
    
    
    
    img_loc = 'item_images/' + item_value
    loc = pag.locateCenterOnScreen(img_loc, confidence = 0.9)
    print(loc)
    
#get_loc_of_item()

is_sold_check()