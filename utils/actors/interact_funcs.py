# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 07:48:16 2024

@author: barna
"""
import pyautogui as pag
import time
from utils.logger import logger as log
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button
from utils.dependents.calc_funcs import MarketCalc
from utils.dependents.dependents import Screen

"""
Creates a parent class to get monitor dimensions to pass to all child classes
that require dimensions, so functions from different locations do not need
to acquire and pass dimensions separately
All interactions are denoted from their respective class by the .act() method
The .act() methods only act. If .act() requires additional input, it must be
passed to the class, not the method.
"""

class Interact(Screen):
    def __init__(self):
        Screen.__init__(self)
        
    def move_to_search(self):
        # Move to Search button
        pag.click(self.winx * 0.938, self.winy * 0.285)
        pag.move(0, self.winy * -0.024, 0.2)
     
    def search_item(self, item):
        # Search and select item
        time.sleep(0.6)
        pag.click(self.winx * 0.094, self.winy * 0.191)
        pag.typewrite(item)
        pag.move(0, self.winy * 0.069, 0.6)
        pag.click()
        pag.move(0, self.winy * 0.031, 0.2)
        pag.click()
        
    def market_refresh(self):
        pag.click(self.winx * 0.938, self.winy * 0.261)
        
    def return_to_market(self):
        pag.click(self.winx * 0.449, self.winy * 0.027)
        pag.move(0, self.winy * 0.083, 0.1)
        pag.click()
        
    def return_to_my_listings(self):
        time.sleep(1.5)
        pag.click(self.winx * 0.547, self.winy * 0.038)
        pag.move(0, self.winy * 0.076, 0.1)
        pag.click()
        time.sleep(0.6)
    
    def check_on_inventory(self):
        pag.click(int(self.winx * 0.6640625), int(self.winy * 0.1736111))
        pag.move(int(self.winx * 0.019531), 0)
        pag.click()
    
    def already_sold_check(self):
        pag.click(self.winx * 0.067, self.winy * 0.01)
        pag.move(0, self.winy * 0.031, 0.1)
        pag.click()
        pag.move(self.winx * 0.479, self.winy * 0.528, 0.3)
        pag.click()

    def buy_sequence(self):
        pag.move(0, self.winy * 0.066, 0.05)
        pag.click()
        time.sleep(.01)
        pag.click(self.winx * 0.5, self.winy * 0.569)
        pag.moveRel(0, self.winy * 0.128)
        pag.click()
        pag.moveRel(0, self.winy * 0.09)
        pag.click()
        time.sleep(0.6)
        pag.moveRel(0, self.winy * -0.208)
        pag.click()
    
    def sell_sequence(self, mktPrice):
        time.sleep(0.3)
        pag.move(self.winx * 0.039, self.winy * -0.458, 0.2)
        pag.click()
        time.sleep(1)
        pag.click(self.winx * 0.768, self.winy * 0.603)
        time.sleep(.1)
        pag.click(self.winx * 0.547, self.winy * 0.576)
        pag.typewrite(mktPrice)
        pag.click(self.winx * 0.498, self.winy * 0.892)
        pag.move(self.winx * -0.039, self.winy * -0.319)
        pag.click()
        
    def first_slot_clear(self):
        # Shift clicking the item out of inventory
        pag.click(self.winx * 0.762, self.winy * 0.556)
        pag.move(0, self.winy * 0.035)
        
        keyboard = KeyboardController()
        mouse = MouseController()
        
        # Hold Shift key
        keyboard.press(Key.shift)
        
        # Perform right-click at specific coordinates
        mouse.click(Button.right)
        
        # Release Shift key
        keyboard.release(Key.shift)
                
        time.sleep(0.5)
    
    def buy_item(self, item):
        
        keyboard = KeyboardController()
        # Clicking the Cancel Trade / Leave Channel button in the case the full
        # stash dialogue box is present
        pag.move(self.winx * -0.479, self.winy * -0.073)
        pag.click()
        pag.move(self.winx * 0.479, self.winy * 0.528, 0.3)
        pag.click()
        
        # The following procedures buy Centaur Tail and moves it.
        # Ensure on Market page
        Interact().return_to_market()
        
        # Searching Centaur Tail
        Interact().search_item(item)
        
        #refreshing page
        Interact().move_to_search()
        Interact().market_refresh()
        time.sleep(0.6)
        
        #Buying Item
        Interact().buy_sequence()
        keyboard.press(Key.esc)
        pag.click(self.winx * 0.547, self.winy * 0.020)
        pag.move(0, self.winy * 0.076, 0.2)
        pag.click()
        time.sleep(1)

        
    def item_search(self, item):
                
        # Ensures on market page
        Interact().return_to_market()
        time.sleep(0.7)
        
        # Search and select Golden Key
        Interact().search_item(item)
        
        #refresh page
        Interact().move_to_search()
        Interact().market_refresh()
    
    def cancel_listing(self, location):
        
        x_value = location[0]
        y_value = location[1]

        pag.click(x_value, y_value)
        pag.click(self.winx * 0.5, self.winy * 0.972)
        pag.move(0, self.winy * -0.347, 0.2)
        pag.click()
        pag.move(int(self.winx * -0.053906), 
                 int(self.winy * -0.0506944), 0.2)
        pag.click()
        
        # Delay between grabbing items - prevents dialogue boxes
        # from stacking
        time.sleep(1.8)
            

    def item_transfer(self, isSoldList, maxKeysCollectable = 10):
        log.notice("Running item_transfer.")
        
        # Reverse list to grab last sold item first, since all items move
        # up after a collect
        isSoldList.reverse()
        for value in isSoldList:
            
            # Variable y value based on what is sold
            x_value = value[0] + 20
            y_value = value[1]
            
            # If the pixel was yellow, click the particular box, click an arbitrary
            # position, then click the "Transfer All Items" button
            if maxKeysCollectable > 0:
                pag.click(x_value, y_value)
                pag.click(self.winx * 0.5, self.winy * 0.972)
                pag.move(0, self.winy * -0.347, 0.2)
                pag.click()
                maxKeysCollectable -= 1
                
                # Delay between grabbing items - prevents dialogue boxes
                # from stacking
                time.sleep(1.5)
                
                # Higher priced items significantly slow down gold transfer
                if MarketCalc().priceCategory == 3:
                    time.sleep(3.5)
                    
            #if the pixel was not yellow, do nothing
            else:
                pass
    
    # Legacy function
    def launch_game(self):
        # Click play from launcher
        pag.click(830, 980)
        log.info("\nLaunching... ")
        # Wait for game to launch
        time.sleep(50)
        
        # Move mouse onto "OK" button on loading screen, click, and 
        # wait for connection
        pag.click(1280, 1080)
        pag.move(0, 40, 0.5)
        pag.click()
        log.info("Waiting for Connection... ")
        pag.sleep(15)
        
        # Enter the lobby on first selected character
        pag.click(1280, 1260)
        pag.move(0, 70, 0.5)
        pag.click()
        log.info("Entering Lobby... ")
        time.sleep(6)
        
        # Go to trade screen
        pag.click(1600, 60)
        pag.move(0, 270, 0.8)
        pag.click()
        time.sleep(2)
        
        # Search and select Golden Key
        pag.click(240, 275)
        pag.typewrite("Golden K")
        pag.move(0, 100, 0.6)
        pag.click()
        
    def sell_items(self, mktPrice, inSlotList, freeSpace):
        log.notice("Running sell_items")
        slotLength = self.winy * 0.038
        posTrackY = 0
        amtSold = 0
        
        for value in inSlotList:
            if amtSold < freeSpace:
                pag.click(value[0], value[1])
                
                #pag.move(0, self.winy * 0.035, 0.3)
                #pag.click()
                time.sleep(0.2)
                pag.click(self.winx * 0.547, self.winy * 0.576)
                time.sleep(0.1)
                pag.typewrite(mktPrice)
                pag.click(self.winx * 0.498, self.winy * 0.892)
                pag.move(self.winx * -0.039, self.winy * -0.319, 0.2)
                pag.click()
                time.sleep(1)
                
                amtSold += 1
            else:
                break
            
    # Removes non-active items from inventory slots by shift-clicking them
    def clear_slots(self, inSlotList, dim: tuple):
        try:
            if inSlotList:
                pass
            
            else:
                keyboard = KeyboardController()
                mouse = MouseController()
                
                slotLength = self.winy * 0.038
                posTrackY = 0
                
                for index, boolean in enumerate(inSlotList):
                    if boolean == False:
                        pag.click(self.winx * 0.762 + slotLength * (dim[0] * index),
                                  self.winy * 0.556 + slotLength * posTrackY)
                        pag.move(0, self.winy * 0.035, 0.2)
                        # Shift-click
                        
                        # Hold Shift key
                        keyboard.press(Key.shift)
                        
                        # Perform right-click at specific coordinates
                        mouse.click(Button.right)
                        
                        # Release Shift key
                        keyboard.release(Key.shift)
                                
                        time.sleep(0.5)
                
                time.sleep(2)
            
        except Exception as e:
            print(f"clear_slots: {e}")