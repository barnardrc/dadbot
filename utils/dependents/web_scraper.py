# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 15:22:49 2024

@author: barna
"""

import re
from urllib.request import urlopen
from utils.logger import logger as log

def webpage_read(url: str):
    
    try:
        page = urlopen(url)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        data = html
        
        return data
    
    except Exception as e:
        log.error(f"webpage_read: {e}")
    


def get_price(data):
    # ReGex expression to find the price data per item
    pattern = r'Marketprice.*?font-size:16px.*?(\d{5}|\d{4}|\d{3}|\d{2})'
    
    try:
        m = re.search(pattern, data)
        price = int(m.group(1))
        
        if price == 16:
            return None
        
        return price
    
    except Exception as e:
        log.error(f"get_price: {e}")

def get_dim(data):
    print(data)

def get_price_category(item, sourceURL = r"https://www.dndprices.com/items/"):
    try:

        # Concatanate strings
        url = sourceURL + item
        
        # data list that contains strings of html text
        data = webpage_read(url)
        
        # Get price from webpage
        price = get_price(data)
        
        log.debug(f"Price: {price}")
        
        return price
    
    except Exception as e:
        log.error(f"get_price_category: {e}")

def get_item_dim(item, sourceURL = r"https://darkanddarker.wiki.spellsandguns.com/"):
    try:        
        suburls = ['Misc', 'Utilities']
        for sub in suburls:
            url = sourceURL + sub
            
            data = webpage_read(url)
            
    except:
        pass
    
def test():
    item = "Troll's Blood"
    print(get_item_dim(item))

#test()