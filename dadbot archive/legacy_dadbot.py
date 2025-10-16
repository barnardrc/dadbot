# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 12:58:35 2024

@author: barna
"""

def main():
    
    # Desired directory for log file:
    logSavePath = r'C:\Users\barna\OneDrive\Documents\1. Documents\01. dadbot'
    log.log_config(logSavePath)
    log.logging.info("\n\n-----Start new Session-----")
    
    # Adjustment metrics
    balAdjItem = "Centaur Tail"
    profitPrice = 18001
    mktPrice = '19499'
    maxSearchTime = 5000
    
    # Init tracking variables
    purchaseAttempt = 0
    timeToBuyTracker = []
    exit_var = 0
    
    if is_game_running() == False:
        interacts.LaunchGame().act()
    
    interacts.GkSearch().act()
    while exit_var < 1:
        
        log.logger.info("\nRunning main... ")
        
        """
        There are two primary roles performed in the main loop: 
            
            1. The balance Check: Prior to each time the balance is checked, it
            is reset to 0. 
            It checks if image capture failed, if any items are
            sold, then if balance is less than the required amount to purchase
            an item.
                If balance is low, or read incorrectly as too low, it increases
                a tracker by the current count, and compares the current
                is_sold_state and balance state with the previous ones.
                If these are the same, it will buy a medium priced item from
                the market to change the balance to something more readable.
                
                If just an item was sold, it attempts to collect gold
                
                Otherwise, the balance is assumed to be correct and it checks
                it will check for items every 1 minute.
        """
        (failedAttempts, 
         balanceCheckTracker, 
         timeToSell,
         maxKeysBuyable) = control.balance_check(profitPrice, 
                                                 item = balAdjItem,
                                                 mktPrice = mktPrice)
                                                 
        print(maxKeysBuyable)
        
        log.logger.info(f"It took {failedAttempts + 1} attempt(s) to acquire balance data.")
        log.logger.info(f'It took {timeToSell} minute(s) for items to sell.')
    
        
        """
        2. The buy / list function: This function checks the last market price
        every .55s until it sees an item it can purchase. Every 100 refreshes 
        it performs the return_to_market interact function. Once an item is 
        purchased, it immediately lists it. 
        This function returns how many refreshes it took until a purchase
        was attempted and whether or not an attempt was made.
        1091 refreshes is about 10 minutes.
        """
        while maxKeysBuyable > 0:
            # Go back to Market screen
            interacts.ReturnToMarket().act()
            interacts.MoveToSearch().act()
            
            # Look for items to buy that meet the criteria
            refreshAmt, didAttempt = control.buy_list_funct(profitPrice, mktPrice, 
                                                    maxSearchTime = 1091)
            
            # Tracking buy / sell times for price adjustment
            if didAttempt:
                purchaseAttempt += 1
            
            timeToBuyTracker.append(refreshAmt)
            if len(timeToBuyTracker) > 9:
                del(timeToBuyTracker[0])
                
            avgBuyTime = calc.avg_buy_time(timeToBuyTracker)
            log.logger.info(f"Purchase attempt #: {purchaseAttempt}")
            log.logger.info(f"Rolling Avg Buy Time: {avgBuyTime} minute(s)")
            
            maxKeysBuyable -= 1
            print(maxKeysBuyable)
            
            # If the market refresh limit was reached, make sure the game is 
            # running
            if refreshAmt == maxSearchTime:
                
                # Continuously attempts to launch game (usually after updates)
                while is_game_running() == False:
                    interacts.LaunchGame().act()
    

main()
#winx, winy = interacts.mon_dimensions()
#overflowState = utils.vision_funcs.item_overflow_check()
#utils.interact_funcs.OverflowFix(overflowState).act()
#utils.interact_funcs.SellItems('20').act()
inSlotList = utils.vision_funcs.gold_key_in_slot()

#utils.interact_funcs.SellItems('19100', inSlotList).act()
#utils.interact_funcs.AlreadySoldCheck().act()
#utils.interact_funcs.ReturnToMarket().act()
