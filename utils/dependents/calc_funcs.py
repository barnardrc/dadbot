# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 13:20:35 2024

@author: barna
"""
import numpy as np
from utils.logger import logger as log
import sys

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class ProfitCalc(metaclass = Singleton):
    def __init__(self, 
                 totalProfit, 
                 itemsBought, 
                 profit, 
                 buyList = [], 
                 sellList = []
                 ):
        
        self.totalProfit = totalProfit
        self.itemsBought = itemsBought
        self.profit = profit
        self.buyList = buyList
        self.sellList = sellList
    
    def __str__(self):
        info = f"""
        
Items Bought: {self.itemsBought}
Profit from Trade: {self.profit}
Total Profit: {self.totalProfit}
        """
        return info
                
    def profit_calc(self, mktPrice: str, price: int) -> int:
        profit = int(int(mktPrice) * 0.95) - price
        
        self.profit = profit
        self.totalProfit += profit
        
        return profit
    
    def increase_items_bought(self):
        self.itemsBought += 1
    
    def add_to_buy_list(self, price = int):
        self.buyList.append(price)
        
    def add_to_sell_list(self, price = int):
        self.sellList.append(price)
    
    def lost_profit_calc(self, mktPrice: str, lastPrice: int) -> int:
        lostProfit = int(int(mktPrice) * 0.95) - lastPrice
        
        self.profit = lostProfit
        
        return lostProfit
    
    def increase_total_profit(self, profit: int, lostProfit: int):
        self.totalProfit = self.totalProfit + profit
    
    # Checks if a number is less than the specified profit price
    def profit_check(self, price: int, profitPrice: int):
        try:
            if price < profitPrice:
                return True
            else:
                return False
        except Exception as e:
            log.error(f"profit_check raised: {e}", exc_info=False)
            pass
        
    # Converts refreshes to minutes and calculates average time on a rolling list
    def avg_buy_time(self, amtRefreshList: list) -> int:
        
        xfrList = []
        # 0.55s / refresh - every 100 refreshes: 1.7s to verify on mkt screen
        for num in amtRefreshList:
            num = ((num*0.55) + ((num/100) * 1.7))//60
            xfrList.append(num)

        total = 0
        for num in xfrList:
            total += num
            
        return round(total / len(xfrList))

    def amt_keys_buyable(self, 
                         balance: int, 
                         profitPrice: int, 
                         mktPrice: str) -> int:
        
        return balance // profitPrice
    
    # Amount of items sold in the trading master panel
    def slotsLeft(self, isSoldList: list) -> int:
        amtSold = 0
        lastSoldPos = []
        
        for i, item in enumerate(reversed(isSoldList)):
            if item:
                amtSold += 1
                lastSoldPos.append(i)
        
        # Amount of slots cleared by transferring money + slots left after the
        # last item that was sold positionally. If nothing is sold, then the 
        # list is empty.
        try:
            amtSold += lastSoldPos[0]
        except:
            log.warning("slotsLeft: Nothing is sold?")
        
        return amtSold
    
    def get_min_balance(self, mktPrice, profitPrice, fee = 0.05, 
                        listPreference = 5
                        ):
        
        listFee = int(int(mktPrice) * fee)
        minBalance = listFee * listPreference + profitPrice
        
        return minBalance

class MarketCalc(metaclass = Singleton):
    def __init__(self, data, priceCatBypass, volatility: int = 5, 
                 minimumVolatility: int = 1, maximumVolatility: int = 20, 
                 volatilityFactor: int = 1, cat1Cutoff = 8000, 
                 cat2Cutoff = 20000, searchTimeMultiplier: int = 25,
                 waitTime = 10):
        
        self.data = data
        self.catBypass = priceCatBypass
        self.volatility = volatility
        self.volMin = minimumVolatility
        self.volMax = maximumVolatility
        self.volFactor = volatilityFactor
        self.priceCategory = 0
        self.cat1Cutoff = cat1Cutoff
        self.cat2Cutoff = cat2Cutoff
        self.searchTimeMultiplier = searchTimeMultiplier
        self.waitTime = waitTime

        
    def update_data(self, newData):
        self.data = newData
    
    # Update the bypass parameter
    def update_cat_bypass(self, state):
        log.notice("Updating Price Category Bypass.")
        self.catBypass = state
        
    # Volatility is an integer between 1 and 20. The more volatility,
    # the lower the max amount of refreshes, which should lead
    # to more price changes.
    def update_volatility(self, 
                          prevBuyPrice: int, 
                          buyPrice: int, 
                          d: float = 0.97
                          ) -> int:
        
        try:
            if (prevBuyPrice != 0 and
            self.volatility <= self.volMax and
            self.volatility >= self.volMin
            ):
                if self.priceCategory == 1 or self.priceCategory == 3:
                    if ((buyPrice < prevBuyPrice - prevBuyPrice * (1 - d) or
                        buyPrice > prevBuyPrice + prevBuyPrice * (1 - d)) and
                        self.volatility != self.volMin
                        ):
                        
                        self.volatility -= 1
                        
                    elif ((buyPrice >= prevBuyPrice - prevBuyPrice * (1 - d) or
                          buyPrice <= prevBuyPrice + prevBuyPrice * (1 - d)) and
                          self.volatility != self.volMax
                          ):
                          
                        self.volatility += 1

                elif self.priceCategory == 2:
                    # Price had to change
                    if (buyPrice != prevBuyPrice and 
                        self.volatility != self.volMin):
                        
                        self.volatility -= 1
                        
                    # Price did not have to change
                    elif (buyPrice == prevBuyPrice and 
                          self.volatility != self.volMax):
                        
                        self.volatility += 1
                    
            else:
                pass

            volView = self.volMax - self.volatility
            #log.debug(f"Updating volatility: {volView}")
            
        
        except Exception as e:
            log.error(f"update_volatility: {e}", exc_info=True)
    
    def update_max_search_time(self):
        maxSearchTime = (self.volatility * 
                         self.searchTimeMultiplier * 
                         self.volFactor)
        
        #log.debug(f"update_max_search_time: volFactor: {self.volFactor}")
        return maxSearchTime
    
    def range_calc(self):
        dataRange = self.data[-1][0] - self.data[0][0]
        return dataRange
    
    # Takes market screen data after formatting, filters data based on price 
    # category, converts it to a more readable format, an np array,
    # then updates the current price info state for the class.
    def get_price_array(self) -> np.ndarray:
        
        filterProtection = False
        #log.debug(f"Price Category: {self.priceCategory}")
        #log.debug(f"self.data: {self.data}")

        try:
            # Initiate filter protection to protect against misreads of 11000's
            for item in self.data:
                for amt in item[1]:
                    if item[0] >= 11000 and item[0] < 12000:
                        filterProtection = True
            
            #log.debug(f"Filter Protection: {filterProtection}")
            list1 = []
            checkList =[]
            for item in self.data:
                #log.debug(f"item: {item}")
                
                if self.catBypass == False:
                    
                    for amt in item[1]:
                        if (self.priceCategory == 1 and 
                            item[0] < self.cat1Cutoff):
                            list1.append(item[0])
                            
                        elif self.priceCategory == 2:
                            if filterProtection:
                                if item[0] > 1000 and item[0] < 2000:
                                    list1.append(item[0] + 10000)
                                elif item[0] < 1000:
                                    list1.append(item[0] + 11000)
                                
                            if (item[0] >= self.cat1Cutoff and
                                item[0] <= self.cat2Cutoff):
                                    list1.append(item[0])
                            
                        elif (self.priceCategory == 3 and
                              item[0] > self.cat2Cutoff):
                            list1.append(item[0])
                            
                        else:
                            pass
                            #log.debug(f"get_price_array could not find a home for: {item[0]}")
                
                # Price category bypass is enabled
                elif self.catBypass:
                    if filterProtection:
                        if item[0] > 1000 and item[0] < 2000:
                            list1.append(item[0] + 10000)
                        elif item[0] < 1000:
                            list1.append(item[0] + 11000)
                        else:
                            list1.append(item[0])
                    else:
                        list1.append(item[0])
                    
            #log.debug(f"Current Prices: {list1}")
            self.priceList = np.array(list1)
            #log.debug(f"arrayed list: {self.priceList}")
            
        except Exception as e:
            log.error(f"get_price_array: {e}")
        
        
    def reject_outliers(self, threshold=3.5):
        """
        Rejects outliers using the Modified Z-Score method with the MAD.
        :param threshold: The Z-score threshold for defining outliers 
        (default: 3.5).
        """
        try:
            # Compute the median
            median = np.median(self.priceList)
            
            # Compute the Median Absolute Deviation (MAD)
            mad = np.median(np.abs(self.priceList - median))
            
            if mad == 0:
                # Prevent division by zero; in this case, treat all values as non-outliers
                log.warning("MAD is zero, no outliers will be identified.")
                self.adjPriceList = self.priceList
                log.debug(f"Original list: {self.priceList}")
                log.debug(f"Adjusted list: {self.adjPriceList}")
                return self.adjPriceList

            # Compute Modified Z-Scores
            modified_z_scores = 0.6745 * (self.priceList - median) / mad
            
            # Filter out outliers
            self.adjPriceList = self.priceList[np.abs(modified_z_scores) <= threshold]
            
            #log.debug(f"Original list: {self.priceList}")
            #log.debug(f"Adjusted list: {self.adjPriceList}")
                
            if len(self.adjPriceList) == 0:
                log.warning("Price Category may be incorrect!", exc_info = False)
            
            return self.adjPriceList

        except Exception as e:
            # Log the function name and the exception details
            log.error(f"Error in function '{self.reject_outliers.__name__}': {e}", exc_info = False)
            
    def update_avg(self):
        self.get_price_array()
        self.reject_outliers()
        self.avg = int(np.average(self.adjPriceList))
        #log.info(f"Average price: {self.avg}")
    
    def get_adjusted_list_length(self):
        x = len(self.adjPriceList)
        #log.debug(f"Adjusted Price list length: {x}")
        
        return x
    
    # Sets price category based off of the passed price
    def set_price_category(self, price: int):
        try:
            if price < self.cat1Cutoff:
                self.priceCategory = 1
            elif price > self.cat2Cutoff:
                self.priceCategory = 3
                self.volFactor = 2
            elif (price >= self.cat1Cutoff and
                  price <= self.cat2Cutoff):
                self.priceCategory = 2
            
            #log.debug(f"Price Category: {self.priceCategory}")
            
        except Exception as e:
            log.warning(f"Set price category failed: {e} : turning on category bypass.", 
                        exc_info=True)
            
            self.update_cat_bypass(True)
    
    # Update price category. Mainly used for debugging
    def update_price_cat(self, newCat):
        self.priceCategory = newCat
    
    # Returns the price category
    def get_price_category(self):
        return self.priceCategory
    
    def update_wait_time(self):
        if self.priceCategory == 3:
            self.waitTime = 30
        elif self.priceCategory < 3:
            self.waitTime = 10
        #log.debug(f"Max Wait Time: {self.waitTime}")
    
    def set_prices(self) -> int:
        try:
            idealBuyPrice = 0
            idealSellPrice = 0
            minProfit = 0
            profit = 0
            
            self.update_avg()
            if self.catBypass:
                self.set_price_category(self.avg)
                self.update_wait_time()
                
            listLength = self.get_adjusted_list_length()
            
            if self.priceCategory == 2:
                x = self.avg % 1000
                idealBuyPrice = self.avg - x - 1000 + 1
                idealSellPrice = self.avg - x + x // 2
                minProfit = idealSellPrice * 0.015
                profit = idealSellPrice * 0.95 - idealBuyPrice
                if profit < minProfit:
                    idealBuyPrice -= minProfit - profit
                
            elif self.priceCategory == 1:
                minProfit = 50
                x = self.avg % 100
                idealBuyPrice = self.avg - x - 100 + 1
                idealSellPrice = self.avg - x + x // 2
                profit = idealSellPrice * 0.95 - idealBuyPrice
                if profit < minProfit:
                    idealBuyPrice -= minProfit - profit
                    
            elif self.priceCategory == 3:
                x = self.avg % 10000
                idealSellPrice = self.avg - x + x // 2
                idealBuyPrice = idealSellPrice * 0.9
                minProfit = idealSellPrice * 0.015
                profit = idealSellPrice * 0.95 - idealBuyPrice
                if profit < minProfit:
                    idealBuyPrice -= minProfit - profit
                    
                
            
            log.debug(f"Buy: {int(idealBuyPrice)} | Sell: {idealSellPrice}")

            return int(idealBuyPrice), idealSellPrice, listLength
        
        except Exception as e:
            log.error(f"set_prices: {e}", exc_info=False) # No exception info
    
    def item_in_slot(inSlotList, expectedColors):
        # transform list to array for masking
        inSlotArray = np.array(inSlotList)
        inSlotArray = np.ma.masked_array(inSlotArray, 
            mask = [item in expectedColors for item in inSlotArray])
        
        return(inSlotArray.mask.tolist())

class DataUtils:
    @staticmethod
    def _get_center(box):
        return (box[0] + box[2] // 2, box[1] + box[3] // 2)
    
    # Finds distance between boxes and rejects any that are within a minimum
    # distance
    @staticmethod
    def filter_close_boxes(locations, min_distance=10):
        unique_locs = []
        for current_loc in locations:
            is_duplicate = False
            cx1, cy1 = DataUtils._get_center(current_loc)
            
            for existing_loc in unique_locs:
                cx2, cy2 = DataUtils._get_center(existing_loc)
                
                distance = ((cx1 - cx2)**2 + (cy1 - cy2)**2)**0.5
                
                if distance < min_distance:
                    is_duplicate = True
                    break
                    
            if not is_duplicate:
                unique_locs.append(current_loc)
        
        if unique_locs:
            return [DataUtils._get_center(item) for item in unique_locs]
        
        else:
            return []