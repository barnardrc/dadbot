# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 12:31:48 2024

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
    totalProfit = 0
    itemsBought = 0
    purchaseAttempt = 0
    timeToBuyTracker = []
    
    if is_game_running() == False:
        interacts.LaunchGame().act()
    
    interacts.GkSearch().act()
    
    log.logger.info("\nRunning main... ")
    
    #
    (failedAttempts, 
     balanceCheckTracker, 
     timeToSell,
     balance
     ) = control.balance_check(
         profitPrice = profitPrice,
         item = balAdjItem,
         mktPrice = mktPrice
         )
    
    maxKeysBuyable = calc.amt_keys_buyable(balance, profitPrice)
    print(maxKeysBuyable)
    
    log.logger.info(f"It took {failedAttempts + 1} attempt(s) to acquire balance data.")

    while maxKeysBuyable > 0:
        
        prevBalance = balance
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
        
        (
        failedAttempts, 
        balanceCheckTracker, 
        timeToSell,
        balance
         ) = control.balance_check(
             profitPrice = profitPrice,
             item = balAdjItem,
             mktPrice = mktPrice,
             )
        
        log.logger.info(f"It took {failedAttempts + 1} attempt(s) to acquire balance data.")
        log.logger.info(f'It took {timeToSell} minute(s) for items to sell.')
        
        profit = prevBalance - balance
        if profit > 0:
            itemsBought += 1
            totalProfit += profit
        
        print(itemsBought)
        print(profit)
        
        maxKeysBuyable = calc.amt_keys_buyable(balance, profitPrice)
        print(maxKeysBuyable)
        
        # If the market refresh limit was reached, make sure the game is 
        # running
        if refreshAmt == maxSearchTime:
            
            # Continuously attempts to launch game (usually after updates)
            while is_game_running() == False:
                interacts.LaunchGame().act()