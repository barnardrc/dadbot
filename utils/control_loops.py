# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 17:12:39 2024

@author: barna
"""

from utils.actors.interact_funcs import Interact
from utils.dependents.exceptions import ExitException
from utils.actors.vision_funcs import DataCapture
import utils.dependents.format_funcs as format_funcs
from utils.dependents.calc_funcs import ProfitCalc, MarketCalc, DataUtils
import utils.dependents.web_scraper as web_scrape
import utils.dependents.json_handler as json_handler
from utils.logger import logger as log
import keyboard
import threading
import sys
import psutil
import time

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Item(metaclass = Singleton):
    def __init__(self,
                 name,
                 rarity,
                 expectedColors = [],
                 dimension = (),
                 is_gold_storage = False,
                 is_stackable = False,
                 max_stack = 0
                 ):
        
        self.name = name
        self.rarity = rarity
        self.formattedName = format_funcs.format_item_for_img_loc(self.name, self.rarity)
        self.expectedColors = expectedColors
        self.dimension = dimension
        self.is_gold_storage = is_gold_storage
        self.is_stackable = is_stackable
        self.max_stack = max_stack
        
        
    def get_dim(self):
        return self.dimension
    
    def update_dimension(self, dim: tuple):
        self.dimension = dim
        
    def set_item_data(self):
        item_data = json_handler.get_item_data(self.formattedName)
        
        self.dimension = item_data[0]
        self.is_gold_storage = item_data[1]
        self.is_stackable = item_data[2]
        self.max_stack = item_data[3]
    

class VariableHandler(metaclass = Singleton):
    def __init__(self,
                 item,
                 balAdjItem,
                 balAdjItemLow,
                 stop_signal,
                 idealBuyPrice = 0,
                 idealSellPrice = 0,
                 balance = 0,
                 maxStash = 0,
                 gccHoldings: int = 10000,
                 scbHoldings: int = 2500,
                 gcbHoldings: int = 1000,
                 gcpHoldings: int = 50,
                 bagAmounts = [],
                 buysBeforeSell = 0,
                 expectedColors = [],
                 maxBuysBeforeSell = 5,
                 maxSearchTime = 125,
                 yPosMulti = 0,
                 freeSpaces = 0
                 ):
        
        self.item = item
        self.balAdjItem = balAdjItem
        self.balAdjItemLow = balAdjItemLow
        self.idealBuyPrice = idealBuyPrice
        self.idealSellPrice = idealSellPrice
        self.balance = balance
        self.maxStash = maxStash
        self.gccHoldings = gccHoldings
        self.scbHoldings = scbHoldings
        self.gcbHoldings = gcbHoldings
        self.gcpHoldings = gcpHoldings
        self.buysBeforeSell = buysBeforeSell
        self.maxBuysBeforeSell = maxBuysBeforeSell,
        self.expectedColors = expectedColors
        self.yPosMulti = yPosMulti
        self.maxSearchTime = maxSearchTime
        self.freeSpaces = freeSpaces
        self.stop_signal = stop_signal
    
    def set_max_buys_before_sell(self):
        if Item().is_gold_storage:
            self.maxBuysBeforeSell = 1
        else:
            self.maxBuysBeforeSell = 1
        
        log.notice(f"Set the maximum amount of buys before a sell to {self.maxBuysBeforeSell}")
        
    def update_free_spaces(self):
        self.freeSpaces = DataCapture().free_spaces_check()
        #log.debug(f"Listing spaces available: {self.freeSpaces}")
        
    def update_max_stash(self, amounts: list) -> int:
        log.info("Running update_max_stash.")
        holdings = [self.gccHoldings, self.scbHoldings, self.gcbHoldings,
                        self.gcpHoldings]
        for amount, holding in zip(amounts, holdings):
            self.maxStash += amount * holding
        log.info(f"Max Stash: {self.maxStash}")
    
    def update_balance(self, failedAttempts):
        self.balance = format_funcs.balance_formatter(
            DataCapture().get_balance(failedAttempts))
        log.info(f"Balance check: {self.balance}")
    def get_max_stash(self):
        return self.maxStash
    
    def get_balance(self):
        return self.balance
    
    def get_prices(self):
        return self.idealBuyPrice, self.idealSellPrice
    
    def get_max_search_time(self):
        return self.maxSearchTime
    
    def get_max_buys_before_sell(self):
        return self.maxBuysBeforeSell
    
    def set_prices(self) -> tuple:
        log.notice("Running set_prices.")
        try:
            
            if VariableHandler().stop_signal.stop: raise ExitException
            
            attempt = 0
            prevBuyPrice = self.idealBuyPrice
            success = False
            while success == False:
                
                if VariableHandler().stop_signal.stop: raise ExitException
                
                Interact().return_to_market()
                Interact().move_to_search()
                Interact().market_refresh()
                time.sleep(0.6)
                
                try:
                    priceCat = MarketCalc().get_price_category()
                    d = DataCapture().get_prices()
                    x = format_funcs.market_data_formatter(d, priceCat)
                
                    MarketCalc().update_data(x)
                    (idealBuyPrice, 
                     idealSellPrice, 
                     listLength) = MarketCalc().set_prices()
                    if listLength >= 2:
                        success = True
                        
                    elif listLength < 2:
                        log.debug(f"Not enough prices: {listLength}")
                        
                        success = False
                        time.sleep(15)
                        
                        attempt += 1
                        if attempt == 5:
                            MarketCalc().update_cat_bypass(True)
                
                except ExitException:
                    raise
                
                except Exception as e:
                    log.error(f"Price update failed in set_prices: {e}",
                              exc_info=False) # Excluding traceback info
                    if not MarketCalc().catBypass:
                        log.debug(f"Will bypass price category in {5 - attempt} attempts")
                        
                    time.sleep(10)
                    
                    if VariableHandler().stop_signal.stop: raise ExitException
                    
                    attempt += 1
                
                if attempt == 5:
                    MarketCalc().update_cat_bypass(True)
                    
                
            # Get new maxSearchTime
            MarketCalc().update_volatility(prevBuyPrice, idealBuyPrice)
            maxSearchTime = MarketCalc().update_max_search_time()
            
            self.idealBuyPrice = idealBuyPrice
            self.idealSellPrice = str(idealSellPrice)
            self.maxSearchTime = maxSearchTime
        
        
        except ExitException:
            raise
            
        except Exception as e:
            print(f"VariableHandler().set_prices() attempt # {attempt}: {e}")
        
        
            
    def get_buys_before_sell(self):
        return self.buysBeforeSell
    
    def increase_buys_before_sell(self):
        self.buysBeforeSell += 1
        log.debug(f"buys until sell: {self.buysBeforeSell}")
    
    def reset_buys_before_sell(self):
        self.buysBeforeSell = 0
        log.debug("Resetting buysBeforeSell Tracker.")
    
    def check_in_slot(self):
        #log.notice("Running check_in_slot.")
        
        itemName = format_funcs.format_item_for_img_loc(
            Item().name, Item().rarity
            )
        
        inSlotList = DataCapture().item_in_slot(itemName)
        filteredInSlotList = DataUtils.filter_close_boxes(inSlotList)
        
        return filteredInSlotList

# Initialize Singleton Classes    
def init_classes(amounts: list, 
                 item: str, 
                 balAdjItem: str, 
                 balAdjItemLow: str,
                 priceCatBypass: bool,
                 dim: tuple,
                 rarity: int,
                 is_gold_storage: bool,
                 is_stackable: bool,
                 max_stack: int,
                 stop_signal: object
                 ) -> None:
    try:
        
        #Initialize classes w/ singleton
        ProfitCalc(totalProfit = 0, itemsBought  = 0, profit = 0)
        MarketCalc(None, priceCatBypass)
        Item(item, rarity = rarity, dimension = dim, 
             is_gold_storage = is_gold_storage, is_stackable = is_stackable,
             max_stack = max_stack)
        VariableHandler(item, balAdjItem, balAdjItemLow, stop_signal)
        VariableHandler().update_max_stash(amounts)
        VariableHandler().set_max_buys_before_sell()
        
        log.notice(f" Market Calc Price Bypass State: {MarketCalc().catBypass}")
        
    except Exception as e:
        log.error(f"init_classes: {e}", exc_info=True)

def init_item(item, formattedItem, hasItem):
    try:
        log.notice("Running init_item.")
        dims = Item().dimension
        
        Interact().return_to_my_listings()
        
        if not hasItem:
            Interact().buy_item(item)
        
        DataCapture().get_item_img(formattedItem, dims)
        
    except Exception as e:
        log.error(f"init_item: {e}", exc_info = True)
        
    
    

# Checks if game process is running
def is_game_running():
    return "Tavern.exe" in (p.name() for p in psutil.process_iter())

# Find sold emblems 
def item_is_sold_check():
    # list of box objects
    soldEmblems = DataCapture().item_is_sold_check()
    filteredListOfEmblems = DataUtils.filter_close_boxes(soldEmblems)
    
    #log.debug(f"Filtered list of sold emblems: {filteredListOfEmblems}")
    return filteredListOfEmblems
        
def set_price_category(item) -> int:
    log.notice("Running set_price_category.")
    """
    Accepts a string that corresponds to the name of an item.
    Returns None, but updates the MarketCalc class with the corresponding
    price category.
    
    Takes the string from the user and goes to the respective URL on 
    dndprices.com to grab the last known price for accurate price 
    categorizing.

    """
    price = web_scrape.get_price_category(item)
    MarketCalc().set_price_category(price)
    MarketCalc().update_wait_time()
    
def collect_sell(soldItems, mktPrice, inSlotList):
    log.notice("Running collect_sell.")
    
    try:
        # limits attempts to collect based off of balance and max gold 
        # able to hold.
        maxKeysCollectable = (
            (VariableHandler().get_max_stash() - 
             VariableHandler().get_balance()
             ) //
             int(mktPrice)
            )
        
        log.debug(f"Max Keys Collectable: {maxKeysCollectable}")
        Interact().item_transfer(soldItems, maxKeysCollectable)
        Interact().already_sold_check()
        VariableHandler().update_free_spaces()
        slotsLeft = VariableHandler().freeSpaces
        Interact().sell_items(mktPrice, inSlotList, slotsLeft)
        log.info(f"Sell: {mktPrice}")
        
        if slotsLeft > 0:
            VariableHandler().reset_buys_before_sell()
        
        
    except Exception as e:
        log.error(f"collect_sell: {e}", exc_info=True)

def restart_sequence():
    VariableHandler().set_prices()

def start_sequence(hasItem = False, itemExists = False):
    
    try:
        item = VariableHandler().item
        rarity = Item().rarity
        formattedItem =  format_funcs.format_item_for_img_loc(item, rarity)
        log.notice("Running Start Sequence.")
  
        try:
            if is_game_running() == False:
                Interact().launch_game()
        except:
            sys.exit("Failed to launch game.")
        
        # Set price category with web scraper
        if MarketCalc().catBypass == False:
            try:
                set_price_category(format_funcs.format_item_for_scrape(item))
            except Exception as e:
                log.error(f"set_price_category failed: {e}")

        if itemExists == False:
            init_item(item, formattedItem, hasItem)
            
            json_handler.item_write(
                formattedItem,
                Item().dimension,
                Item().is_gold_storage,
                Item().is_stackable,
                Item().max_stack
                )
            
            # Initial search
            Interact().item_search(item)
            time.sleep(0.6)
            if VariableHandler().stop_signal.stop: raise ExitException
            
        elif itemExists:
            
            # Initial search
            Interact().item_search(item)
            time.sleep(0.6)
            if VariableHandler().stop_signal.stop: raise ExitException
            
            # No need to clear slots if item data needed to be captured.
            Interact().return_to_my_listings()
            Interact().check_on_inventory()
            inSlotList = VariableHandler().check_in_slot()
            #log.debug(f"inSlotList returned: {inSlotList}")
            #Interact().clear_slots(inSlotList, Item().get_dim())
        
        # Initialize amt of free spaces
        VariableHandler().update_free_spaces()
        # set prices
        VariableHandler().set_prices()
    
    except ExitException:
        raise
    
    except Exception as e:
        log.error(f"start_sequence: {e}", exc_info=True)
        
# When market price is below listed items price, but sell page is full.
# It may be necessary to clear market spaces and 
def move_price_down(amtToChange=1, changeThreshold = 0.05):
    try:
        log.notice("Running move_price_down.")
        priceCat = MarketCalc().get_price_category()
        prevBuyPrice, prevSellPrice = VariableHandler().get_prices()
        
        # Find new quicksell price
        VariableHandler().set_prices()
        idealBuyPrice, idealSellPrice = VariableHandler().get_prices()
        
        # Ensure prices are updated and persistent
        log.debug(f"Updated Prices: Buy - {idealBuyPrice}, Sell - {idealSellPrice}")
        
        def cancel_and_relist():
            log.info("Moving price down.")
            Interact().return_to_my_listings()
            Interact().cancel_listing(amtToChange)
            inSlotList = VariableHandler().check_in_slot()
            
            # List items at the new price
            Interact().sell_items(idealSellPrice, inSlotList, amtToChange)
            VariableHandler().reset_buys_before_sell()
            
        if (priceCat <= 1 and 
            idealBuyPrice < (prevBuyPrice * (1 - changeThreshold))
            ):
            cancel_and_relist()
        
        elif priceCat > 1 and idealBuyPrice < prevBuyPrice:
            cancel_and_relist()
        
        else:
            log.info("Price did not need to move.")

    except Exception as e:
        log.error(f"move_price_down: {e}", exc_info=True)
    
def buy_sell(maxKeysBuyable, purchaseAttempt = 0,
             totalProfit = 0, itemsBought = 0, timeToBuyTracker = [],
             failedPurchase = 0
             ):
    log.notice("Running buy_sell.")
    
    try:
        
        if VariableHandler().stop_signal.stop: raise ExitException
        
        while maxKeysBuyable > 0:
            
            if VariableHandler().stop_signal.stop: raise ExitException
            
            profitPrice, mktPrice = VariableHandler().get_prices()
            maxSearchTime = VariableHandler().get_max_search_time()
            log.debug(f"Max search time: {maxSearchTime}\n")
            prevBalance = VariableHandler().get_balance()
            
            # Go back to Market screen
            Interact().return_to_market()
            Interact().move_to_search()
            
            # Look for items to buy that meet the criteria
            refreshAmt, didAttempt, price = buy_attempt_funct()
            
            # Tracking buy / sell times for price adjustment
            if didAttempt:
                purchaseAttempt += 1
                # There is a dialogue box that covers the "My Listings" tab
                # after a successful purchase
                time.sleep(0.6)
        
            timeToBuyTracker.append(refreshAmt)
            if len(timeToBuyTracker) > 9:
                del(timeToBuyTracker[0])
                
            avgBuyTime = ProfitCalc().avg_buy_time(timeToBuyTracker)
            #log.debug(f"Purchase attempt #: {purchaseAttempt}")
            log.info(f"Rolling Avg Buy Time: {avgBuyTime} minute(s)")
            
            if failedPurchase > 5:
                log.info("Failed purchases greater than 5, changing balance...")
                Interact().buy_item(VariableHandler().balAdjItemLow)
                Interact().item_search(VariableHandler().item)
                failedPurchase = 0
            
            (
            failedAttempts, 
            balanceCheckTracker,
            timeToSell,
            lostProfit,
            maxKeysBuyable,
            didSell
             ) = balance_check(
                 lastPrice = price
                 )
            
            log.debug(f"It took {failedAttempts + 1} attempt(s) to acquire balance data.")
            log.info(f'It took {timeToSell} minute(s) for items to sell.')
            
            # Track whether or not a purchase attempt was successful
            balanceDiff = prevBalance - VariableHandler().get_balance()
            
            if balanceDiff > 0 and didAttempt:
                ProfitCalc().increase_items_bought()
                VariableHandler().increase_buys_before_sell()
                ProfitCalc().profit_calc(mktPrice, price)
                ProfitCalc().add_to_buy_list(price)
                failedPurchase = 0
                log.info(f"Buy: {price}")
                
            elif balanceDiff == 0 and refreshAmt != maxSearchTime:
                failedPurchase += 1
                log.debug(f"Failed purchase #: {failedPurchase}")
            
            if (VariableHandler().get_buys_before_sell() >=
                VariableHandler().get_max_buys_before_sell()
                ):
                
                Interact().return_to_my_listings()
                inSlotList = VariableHandler().check_in_slot()
                soldItems = item_is_sold_check()
                slotsLeft = VariableHandler().freeSpaces
                collect_sell(soldItems, mktPrice, inSlotList)
                Interact().return_to_market()
                
            if failedPurchase > 5:
                log.info("Failed purchases greater than 5, changing balance...")
                Interact().buy_item(VariableHandler().balAdjItemLow)
                Interact().item_search(VariableHandler().item)
                failedPurchase = 0
                
    
            if didSell or refreshAmt == maxSearchTime or refreshAmt <= 5:
                VariableHandler().set_prices()
                
    except ExitException:
        raise
        
    except Exception as e:
        log.error(f"buy_sell: {e}", exc_info=True)
    
def buy_attempt_funct():
    log.notice("Running buy_attempt_funct.")
    try:
        profitPrice, mktPrice = VariableHandler().get_prices()
        maxSearchTime = VariableHandler().get_max_search_time()
        didAttempt = False
        # initial refresh to prevent bot from attempting to buy the same item twice
        Interact().market_refresh()
        time.sleep(1)
        
        i = 0
        while i < maxSearchTime:
    
            i += 1
            
            Interact().market_refresh()
            
            time.sleep(0.55)
            
            if VariableHandler().stop_signal.stop: raise ExitException
        
            price = format_funcs.price_formatter(DataCapture().price_grab())
            # If stuck on listings page due to dungeon change dialogue box
            if type(price) == str:
                time.sleep(2)
                Interact().return_to_market()
                log.warning(f"Formatter Returned '{price}' as the price.")
            # Efficiency Checking
            # print(price)
            if price == 1211:
                pass
            # Check if last price is profitable
            elif ProfitCalc().profit_check(price, profitPrice):
                
                # Execute the buy and sell sequence
                Interact().buy_sequence()
                didAttempt = True
                log.info(f'A buy sequence was executed at {price} after {i} refreshes.')
                log.debug(f"Buy sequence at {price}")
                Interact().already_sold_check()
                
                #Exit
                break
            
        if i == maxSearchTime:
            log.info(f"No buys were attempted for {i} refreshes...")
        
        return i, didAttempt, price
    
    except ExitException:
        raise
    
    except Exception as e:
        log.error(f"buy_attempt_func: {e}", exc_info=True)
        
def balance_check( 
                  lastPrice = 0, 
                  balanceCheckTracker = 0,
                  failedAttempts = 0, 
                  prevBalance = 0, 
                  timeToSell = 0,
                  lostProfit = 0,
                  goldXfrAttempt = 0,
                  prevSoldState = False,
                  didSell = None,
                  ):
    
    log.notice("Running balance_check.")
    try:
        if VariableHandler().stop_signal.stop: raise ExitException
        
        priceCategory = MarketCalc().get_price_category()
        profitPrice, mktPrice = VariableHandler().get_prices()
        # The balance check loop
        # Return to my listings tab before balance check and waits
        
        Interact().return_to_my_listings()
        VariableHandler().update_balance(failedAttempts)
        minBalance = ProfitCalc().get_min_balance(mktPrice, profitPrice)
        log.debug(f"Minimum balance: {minBalance}")
        
        while VariableHandler().get_balance() < minBalance:
            
            if VariableHandler().stop_signal.stop: raise ExitException
            
            profitPrice, mktPrice = VariableHandler().get_prices()

            Interact().return_to_my_listings()
            balance = VariableHandler().get_balance()
            inSlotList = VariableHandler().check_in_slot()
            soldItems = item_is_sold_check()
            slotsLeft = VariableHandler().freeSpaces
            isItemSold = any(soldItems)
            sellAttempt = False
            
            # If a balance check fails, it will attempt to acquire 
            # sold items to change the balance number
            if balance == -1:
                if isItemSold != prevSoldState:
                    log.debug("Could not read balance - profit may be incorrect now...")
                    Interact().item_transfer(soldItems)
                    Interact().already_sold_check()
                    Interact().sell_items(mktPrice, inSlotList, slotsLeft)
                    VariableHandler().reset_buys_before_sell()
                    sellAttempt = True
                
                elif any(inSlotList):
                    Interact().sell_items(mktPrice, inSlotList, slotsLeft)
                    VariableHandler().reset_buys_before_sell()
                    sellAttempt = True
                
                # Balance cannot be read after several attempts and no item is sold
                elif  (failedAttempts > 18 and 
                       isItemSold == prevSoldState):
                    
                    if priceCategory > 1:
                        Interact().buy_item(VariableHandler().balAdjItem)
                    elif priceCategory == 1:
                        Interact().buy_item(VariableHandler().balAdjItemLow)
                    
                    Interact().item_search(VariableHandler().item)
                    
                    # Reset attempts
                    failedAttempts = 0
                    
                else:
                    failedAttempts += 1
                
            elif balance < minBalance:
                balanceCheckTracker += 1
                
                #print(f"Balance Check Tracker: {balanceCheckTracker}")
                
                # If balance cannot change, but is higher than profitPrice, and
                # is being misread, it will buy an item to intentionally change
                # the balance
                if (
                    balanceCheckTracker > 1 and
                    prevSoldState == True and
                    balance == prevBalance
                    ):
                    
                    Interact().buy_item(VariableHandler().balAdjItem)
                    Interact().item_search(VariableHandler().item)
                    
                elif isItemSold:
                    # Will lose profit if balance check transfers item
                    lostProfit = (ProfitCalc().lost_profit_calc(
                        mktPrice, lastPrice)
                        )
                    ProfitCalc().increase_items_bought()
                    VariableHandler().increase_buys_before_sell()
                    
                    collect_sell(soldItems, mktPrice, inSlotList)
                    goldXfrAttempt += 1
                    
                    if goldXfrAttempt > 1:
                        log.warning("Not enough storage to trade items!")
                    sellAttempt = True
                    
                else:
                    waitTime = MarketCalc().waitTime
                    log.debug(f"Balance Check #: {balanceCheckTracker}")
                    if balanceCheckTracker == 1 and isItemSold:
                        Interact().sell_items(mktPrice, inSlotList, slotsLeft)
                        for slot in slotsLeft:
                            log.info(f"Sell: {mktPrice}")
                        VariableHandler().reset_buys_before_sell()
                    
                    # Check if price needs to change based on price category
                    elif balanceCheckTracker % waitTime == 0:
                        move_price_down()
                        sellAttempt = True
                            
                    else:
                        # Force items to list
                        if balanceCheckTracker == 1:
                            Interact().sell_items(mktPrice, inSlotList, slotsLeft)
                            VariableHandler().reset_buys_before_sell()
                        log.info(f"Have waited for {balanceCheckTracker} minutes...")
                        timeToSell += 1
                        sellAttempt = True
                        time.sleep(60)
                        
            # Variables to track states of last loop
            prevSoldState = isItemSold
            prevBalance = balance
            
            # reset balance
            VariableHandler().update_balance(failedAttempts)
            profitPrice, mktPrice = VariableHandler().get_prices()
            minBalance = ProfitCalc().get_min_balance(mktPrice, profitPrice)
            if sellAttempt:
                didSell = True
        
        maxKeysBuyable = (
            ProfitCalc().amt_keys_buyable(
                VariableHandler().get_balance(), 
                profitPrice, 
                mktPrice
                ))
        
        if VariableHandler().stop_signal.stop: raise ExitException
        
        log.notice(f"{ProfitCalc()}")
        
        return (
            failedAttempts, 
            balanceCheckTracker, 
            timeToSell, 
            lostProfit,
            maxKeysBuyable,
            didSell
            )
    
    except ExitException:
        raise
    
    except Exception as e:
        log.error(f"balance_check: {e}", exc_info=True)
        

"""

------------------Testing Environment------------

"""

def vision_test():
    print(DataCapture().item_in_slot(Item().get_dim()))
    x = DataCapture().free_spaces_check()
    print(x)
    
def interact_test(var1, var2, var3):
    Interact().sell_items(var1, var2, var3)
    
def calc_test():
    VariableHandler().set_prices()
    
def test():
    pass