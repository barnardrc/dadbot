# -*- coding: utf-8 -*-
"""
Created on Sun Oct 12 18:53:42 2025

@author: barna
"""
from tkinter import ttk
import tkinter as tk
from pathlib import Path
from utils.ui_utils.file_handler import get_ui_elements
from PIL import Image, ImageTk


_pil_image_cache = {}
_tk_image_cache = {}

def load_styles(root):
    CUSTOM_THUMB = 'Image.Vertical.TScrollbar'
    stem_to_path = get_ui_elements()
    style = ttk.Style(root)
    
    try:
        style.theme_use('clam')
        
    except tk.TclError:
        pass
    
    if not hasattr(root, '_image_references'):
        root._image_references = {}
    
    
    
    _pil_image_loaded = {key: Image.open(value) for key, value in stem_to_path.items()}
    _pil_image_cache.update(_pil_image_loaded)
    for key, pil_img in _pil_image_cache.items():
        root._image_references[key] = ImageTk.PhotoImage(pil_img)
    
    # Define custom colors for the scrollbar
    SCROLLBAR_COLOR = '#B62EFF'  # Dark color for the thumb/thumb border
    TROUGH_COLOR = '#21356E'     # Background color of the scroll area
    BACKGROUND_COLOR = '#1F232D'
    
    # 1. Custom Thumb
    style.element_create(
        'img_thumb',         # Name of the custom element
        'image',             # Element type
        root._image_references['scroll_bar'],     # Default image
        # State mapping: (element name, [states], image variable)
        ('active', root._image_references['scroll_bar_active']), # Image when mouse is over it
        border=[0, 0, 0, 0],       # Image border/padding
        sticky='nsew'          # Stretch horizontally
    )
    
    # --- Scrollbar Customization ---
    # 1. Define the custom style inheriting from 'TScrollbar'
    style.configure(
        CUSTOM_THUMB,
        background=SCROLLBAR_COLOR, # Color of the thumb/border area
        troughcolor=TROUGH_COLOR,   # Color of the track/trough
        bordercolor=TROUGH_COLOR,   # Make the scrollbar border match the trough
        padding=[0, 0],
        arrowsize = 15
    )

    # 2. Configure the Thumb (the movable part)
    style.map(
        CUSTOM_THUMB,
        # Change the thumb color when the mouse hovers over it
        background=[('active', '#5A667A')]
    )
    
    style.layout(
        CUSTOM_THUMB,
        [
            # 3. The Trough (The track)
            ('Vertical.Scrollbar.trough', {'sticky': 'nsew', 'children': [
                
                # 4. The Thumb (Movable Slider)
                # The thumb element is nested inside the trough
                ('Vertical.Scrollbar.thumb', {'expand': 1, 'sticky': 'nswe', 'children': [
                    # Use your custom image element here
                    ('img_thumb', {'sticky': 'nsew'}) 
                ]})
            ]})
        ]
    )
    
    style.configure(
        'ImageContainer.TFrame',
        background = BACKGROUND_COLOR,
        relief = 'flat',
        borderwidth = 0
        )