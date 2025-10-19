# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 12:17:34 2024

@author: barna
"""

# Imports

import utils.control_loops as control
from utils.logger import logger as log
from utils.dependents.exceptions import ExitException, FullExitException
from ui import UIManager, start_ui
import tkinter as tk
import threading
from queue import Queue
import keyboard

# create key monitor for seamless escape
class KeyMonitor:
    def __init__(self):
        self.stop = False
        self.do_test = False
        
def key_monitor(signal_object):
    log.notice("Press 'Q' to stop.")
    
    while not signal_object.stop:
        event = keyboard.read_event()
        
        if event.event_type == keyboard.KEY_DOWN:
            
            if event.name == 'q':
                signal_object.stop = True
                log.notice("Exit input ('q') detected - Finishing process and exiting...")
                break

            elif event.name == 't':
                # Check if the 'ctrl' key is also held down
                if keyboard.is_pressed('ctrl'):
                    log.notice("Hotkey 'Ctrl+T' detected.")
                    signal_object.do_test = True

    log.notice("Key monitor thread finished.")
    
def run_test():
    control.move_price_down(amtToChange = 2)
    
    
def bot_app(item,
             previous_item,
             amounts,
             balAdjItem,
             balAdjItemLow,
             priceCatBypass,
             dim,
             rarity,
             is_gold_storage,
             is_stackable,
             max_stack,
             signals,
             hasItem,
             itemExists,
             test_env
             ):
    
    try:
        log.notice("Running bot_app.")
        
        if item != previous_item:
            # Initialize classes and run start sequence
            control.init_classes(amounts,
                                 item,
                                 balAdjItem,
                                 balAdjItemLow,
                                 priceCatBypass,
                                 dim,
                                 rarity,
                                 is_gold_storage,
                                 is_stackable,
                                 max_stack,
                                 signals
                                 )
            
            control.start_sequence(hasItem, itemExists)
            
        else:
            control.restart_sequence()

        if not test_env:
            # initial balance check
            (failedAttempts, balanceCheckTracker, timeToSell, lostProfit,
             maxKeysBuyable, didSell) = control.balance_check(
            )
                
            #Begin control loops
            control.buy_sell(
                maxKeysBuyable = maxKeysBuyable
                )
            
        elif test_env:
            run_test()
            
    except ExitException:
        log.notice("Exit complete!")
    
    except Exception as e:
        log.error(f"An error occured during execution: {e}", exc_info = True)
    
def main():
    signals = KeyMonitor()
    root = tk.Tk()
    
    log.setLevel('DEBUG')
    log.info("\n\n-----Start new Session-----")
    
    try:
        previous_item = None
        
        # Keyboard monitoring thread
        monitor_thread = threading.Thread(target=key_monitor,
                                          args = (signals,),
                                          daemon = True
                                          )
        
        monitor_thread.start()
        
        # Amount of gold storage the user has
        gccAmount = 0
        scbAmount = 0
        gcbAmount = 0
        gcpAmount = 720
        amounts = [gccAmount, scbAmount, gcbAmount, gcpAmount]
        
        # Start UI
        app_manager = start_ui(root, bot_start_callback = bot_app,
                               signals = signals)
    
    except Exception as e:
        log.error(f"An error occured during execution: {e}", exc_info = True)



""" ##########################################################################
    
# ---------------- TEST --------------- #

########################################################################## """

def vision_test():
    control.vision_test()

if __name__ == "__main__":
    vision_test()