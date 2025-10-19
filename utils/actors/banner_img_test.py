# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 12:45:49 2025

@author: barna
"""

import pathlib
import pyautogui as pag
import pyscreeze
from utils.dependents.calc_funcs import DataUtils

pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION = False


def find_img():
    troll_pelt = 'troll_pelt_4_banner.png'
    scb = 'spectral_coinbag_7_banner.png'
    gcb = 'gold_coin_bag_7_banner.png'
    list_item_banner = 'list_item_banner.png'
    
    
    current_dir = pathlib.Path(__file__).parent
    folder = 'banner_images'
    img_loc = current_dir / folder / list_item_banner

    img_loc = str(img_loc)
    
    allSpaces = pag.locateAllOnScreen(img_loc, confidence = 0.7)

    
    return allSpaces

def main():
    img = find_img()
    
    imgs = list(img)
    
    filtered_boxes = DataUtils.filter_close_boxes(imgs)
    
    print(filtered_boxes)

main()