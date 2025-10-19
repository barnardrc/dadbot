# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 13:23:20 2024

@author: barna
"""

import regex as re
from collections import defaultdict
from utils.logger import logger as log

def balance_formatter(string): # --> int()
    """
    Takes the number captured from the screen in the balance location and
    attempts to format it as an integer. 
    """
    stripped_string = string.replace(',', '').strip()
    num_list = []
    
    for char in stripped_string:
        try:
            num_list.append(int(char))
        except:
            pass
    
    s = [str(i) for i in num_list]
    num = "".join(s)
    
    try:
        number = int(num)
        return number
    
    except:
        log.debug(f'Balance check failed! Info collected: "{num}"')
                    
        return -1
    
# takes the price string captured from the price checker and reformats it
def price_formatter(p) -> int:
    # List of undesired chars that appear at beginning because of art
    nonChars = ['&', '@', 'B']
    
    #replace the comma and remove whitespace
    price = p.replace(',', '')
    price = price.strip()
    
    # It is common for pyt to read the leading gold coins as an additional 
    # number or a special character, but the rest correctly. Since there are no
    # 6 digit numbers, this corrects for that.
    try:
        if len(price) == 6 or price[0] in nonChars:
            price = price[1:]
    except:
        pass
    
    # It's fine if the string acquired captures a non-int, then it will 
    # just not be evaluated:
    try:
        price = int(price)
    except:
        pass
    
    return price

def new_market_data_formatter(times, totals, stacked_prices, priceCat = None) -> dict():
    tll = []
    priceList = []
    timeList = []
    
    

# Takes string from vision function of times and prices on market page and
# converts them to a defaultdict
def market_data_formatter(d, priceCat = None) -> dict():
    # Seach Expressions
    priceExpression = r'(.*\D)(\d+)'
    #Finds all the time expressions
    timeExpression = r'( )(6d )(.*m)'
    #Extracts the last two integer strings from the time expression
    hourMinExpression = r'\d+'
    
    #init lists
    tll = []
    priceList = []
    timeList = []
    
    #split the data by lines
    data = d.split('\n')
    #Extract time and price data and format price data
    for line in data:
        try:
            # Price gathering search
            line = line.replace(',', '')
            price = re.search(priceExpression, line)
            log.debug(f"Price search returns: {price}")
            price = price.group(2)
            log.debug(f"Group 2 in search: {price}")
            if len(price) > 5:
                priceList.append(int(price[1:]))
                
            elif (len(price) < 6 and 
                  len(price) > 2 and
                  price != '888'
                  ):
                priceList.append(int(price))
            
            # Time gathering search
            m = re.findall(hourMinExpression, line)
            for item in m:
                m[m.index(item)] = int(item)
            try:
                # Formatting hr:mm as minutes
                timeListed = (60 - m[2]) + (24 - m[1] - 1) * 60
                if timeListed > 0:
                    tll.append(timeListed)
            except:
                pass
            
        except:
            pass
        

    # Creating the dictionary
    zippedkv = list(zip(priceList, tll))
    time_to_price = defaultdict(list)
    
    for k, v in zippedkv:
        time_to_price[k].append(v)
    
    return sorted(time_to_price.items())

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
    
    # Check if already formatted
    if isinstance(rarity, int):
        return rarity
        
    if rarity:
        rarity_key = rarity.lower()
    
        val = RARITY_MAPPING.get(rarity_key)
        
        return val
    
    else:
        return 0
    
    
def format_item_from_img_loc(item_png : str):
    item = item_png.replace('_', ' ')
    item = item[:-11].title()
    
    try:
        rarity = int(item[-1])
    except Exception as e:
        log.error(f"Error formatting UI item: {e}")
    
    item = item[:-2]
    
    
    return item, rarity
    
def format_item_for_img_loc(item: str, rarity: int = None):
    item = item.lower()
    item = item.replace(' ', '_')
    rarity = get_rarity(rarity)
    
    if rarity is not None:
        item = item + '_' + str(rarity)
    return item + '.png'

# Takes formatted item (from json or for saving) and adds banner for banner
# locating
def format_item_for_banner_loc(item: str):
    if item[-4:] == '.png':
        parts = item.split('.')
        formatted_item = parts[0] + '_banner.' + parts[1]
    elif '.' not in item:
        formatted_item = item + '_banner' + '.png'
    else:
        raise ValueError("Cannot format item for listing detection!")
    log.debug(f"formatting item: {formatted_item}")
    return formatted_item

def format_item_for_scrape(item_name):
    try:
        item = item_name.lower().replace(' ', '_').replace("'", '')
        
        return item
    except Exception as e:
        log.error(f"format_item_name: {e}")