# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 15:20:33 2024

@author: barna
"""
from PIL import Image
from utils.dependents.dependents import Screen
from utils.logger import logger as log
import pathlib
import mss
import pytesseract as pyt
import cv2
import numpy as np
import pyscreeze
import pyautogui as pag

pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION = False
pyt.pytesseract.tesseract_cmd = r'C:\Users\barna\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
MON_NUM = 2

class DataCapture(Screen):
    def __init__(self):
        Screen.__init__(self)
        current_dir = pathlib.Path(__file__).parent
        
        self.pytConfig = "--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.imgs_loc = current_dir / 'item_images'
        
        # [Top, Left, Width, Height]
        self.inventory_region_ratios = [0.574, 0.751, 0.216, 0.192]
        self.list_region_ratios = [0.458, 0.014, 0.284, 0.521]
        
        # [Width, Height]
        self.inv_slot_dim_ratios = [0.022, 0.039]
        
    # The images and all filtering are currently optimized for expected input
    # from non-binarized images
    def preprocess_image(self, img):
        img = np.array(img)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        return Image.fromarray(binary)
    
    def get_text(self, sct_img):
        # Extract text
        try:
            text = pyt.image_to_string(sct_img)
            #log.debug(text)
            
        except Exception as e:
            log.error(f"OCR failed: {e}")
            text = ''
        
        return text
    
    # Gets the capture region using passed ratios for static screen grabs.
    def get_capture_region(self, region_ratios = None, 
                           region_pixels = None, 
                           monitor_number = MON_NUM,
                           ocr = False,
                           save_name = None
                           ):
        #log.notice("Running get_capture_region.")
        
        with mss.mss() as sct:
            # Validate region input
            if region_ratios:
                #log.debug("Setting capture region.")
                monitor = {
                    "top": int(self.winy * region_ratios[0]),
                    "left": int(self.winx * region_ratios[1]),
                    "width": int(self.winx * region_ratios[2]),
                    "height": int(self.winy * region_ratios[3]),
                    "mon": monitor_number,
                }
                
            elif region_pixels:
                monitor = {
                    "top": region_pixels[0],
                    "left": region_pixels[1],
                    "width": region_pixels[2],
                    "height": region_pixels[3],
                    "mon": monitor_number,
                }
                
            else:
                raise ValueError("Either region_ratios or region_pixels must be provided.")
            
            # Capture the region
            sct_img = sct.grab(monitor)
            
            # Perform in-memory computation
            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        
        if save_name:
            output_loc = self.imgs_loc / save_name
            output_loc = str(output_loc) + '.png'
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=output_loc)
            log.debug(f"Item img saved to {self.imgs_loc}")
        
        if ocr:
            return self.get_text(img)
    
    def check_item_img(self):
        pass
    
    def get_item_img(self, item: str, dims: tuple):
        w, h = self.inv_slot_dim_ratios
        
        top = self.inventory_region_ratios[0]
        left = self.inventory_region_ratios[1]
        width = w * dims[0]
        height = h * dims[1]
        
        region_ratios = [top, left, width, height]
        
        self.get_capture_region(region_ratios = region_ratios, save_name = item)
        
    def get_prices(self, ocr = True):
        log.notice("Running get_prices.")
        region_ratios = [0.308, 0.640, 0.393, 0.591]
        d = self.get_capture_region(region_ratios = region_ratios, ocr = ocr)
        
        return d
    
    #Captures the part of the screen with the last, lowest listed price and
    # converts it to a string
    def price_grab(self, ocr = True):
        region_ratios = [0.313, 0.762, 0.049, 0.035]
        p = self.get_capture_region(region_ratios = region_ratios, ocr = ocr)
        
        return p

    def get_balance(self, attempt = 0, ocr = True):
        
        # Changes width parameter of capture window based off of attempts whenever
        # balance_formatter returns -1. This assists in capturing the text when it is
        # different lengths.
        adjusted_region = [
            0.915,
            0.939 - 0.001 * attempt,  # Adjust left based on attempt
            0.031 + 0.004 * attempt,  # Adjust width based on attempt
            0.024,
        ]
        
        return self.get_capture_region(region_ratios = adjusted_region, ocr = ocr)
        
    def is_inventory_empty(self):
        target_area = '/empty_trade_screen.png'
        img_loc = self.imgs_loc / target_area
        
        loc = pag.locateOnScreen(str(img_loc), confidence = 0.90)
        
        if loc:
            return False
        else:
            return True
        
    # Finds all instances of the emblem that is associated with an item being sold
    # This funct will require additional sorting to filter out duplicates.
    # Returns a list of Box objects from pyautogui
    def item_is_sold_check(self):
        target_area = 'sold_emblem.png'

        img_loc = self.imgs_loc / target_area
        #log.debug(f"Path for sold emblem: {str(img_loc)}")
        isSoldList = pag.locateAllOnScreen(str(img_loc), confidence = 0.9)
              
        if isSoldList is not None:
            return list(isSoldList)
        else:
            return []
 
    def item_in_slot(self, item):
        
        img_loc = self.imgs_loc / item
        img_loc = str(img_loc) + '.png'
        #ratios = self.inventory_region_ratios
        
        #top = int(ratios[0] * self.winy)
        #left = int(ratios[1] * self.winx)
        #width = int(ratios[2] * self.winx)
        #height = int(ratios[3] * self.winy)
        
        inSlotList = pag.locateAllOnScreen(img_loc, confidence = 0.9)
        
        if inSlotList is not None:
            return list(inSlotList)
        else:
            return []

    def free_spaces_check(self):
        
        freeSpaces = 0
        rejectedColors = [29, 30, 31, 32]
        
        with mss.mss() as sct:
            # Get information of monitor 2
            monitor_number = MON_NUM
            mon = sct.monitors[monitor_number]
            
            count = 0
            for i in range(
                           int(self.winy * 0.495),
                           int(self.winy * 0.938),
                           int(self.winy * 0.047)
                           ):
                
                # The distance between mkt boxes is not constant
                count += 1
                if count > 4:
                    i -= 10
                # The screen part to capture
                monitor = {
                    "top": i,
                    "left": int(self.winx * 0.0390625),
                    "width": 1,
                    "height": 1,
                    "mon": monitor_number,
                }
                output = "sell_check-mon{mon}_{top}x{left}_{width}x{height}.png".format(**monitor)
            
                # Grab the data
                sct_img = sct.grab(monitor)
            
                # Save to the picture file
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        
                color = img.getcolors()
                
                img.close()
                
                if color[0][1][0] in rejectedColors:
                    freeSpaces += 1
            
        return freeSpaces