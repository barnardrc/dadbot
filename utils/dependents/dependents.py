# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 13:01:29 2024

@author: barna
"""
import ctypes

class Screen():
    def __init__(self):
        user32 = ctypes.windll.user32
        
        self.winx = user32.GetSystemMetrics(0)
        self.winy = user32.GetSystemMetrics(1)
        self.monitors = user32.GetSystemMetrics(80)
        
    def print_dimensions(self):
        print(self.winx)
        print(self.winy)

    def num_monitors(self):
        print(self.monitors)