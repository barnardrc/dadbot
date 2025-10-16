# -*- coding: utf-8 -*-
"""
Created on Sun Oct 12 18:19:39 2025

@author: barna
"""
from PIL import ImageTk, Image
from pathlib import Path
import tkinter as tk
from tkinter import ttk

class ImageListApp:
    def __init__(self, master, image_paths, selection_callback):
        self.master = master
        self.image_paths = image_paths
        self.selected_item = tk.StringVar()
        self.selection_callback = selection_callback
        
        # --- Main Frame and Scrollbar ---
        main_frame = ttk.Frame(master, style = 'ImageContainer.TFrame')
        main_frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # 1. Create the Canvas (The viewport)
        self.canvas = tk.Canvas(main_frame, borderwidth=0, background = '#1F232D',
                                highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # 2. Create the Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview,
                                  style='Image.Vertical.TScrollbar')
        
        scrollbar.pack(side="right", fill="y")
        
        # 3. Link the Scrollbar to the Canvas
        self.canvas.config(yscrollcommand=scrollbar.set)

        # 4. Create the Interior Frame (The actual scrolling content holder)
        # This is where we will pack all our banner images
        self.interior_frame = ttk.Frame(self.canvas, style='ImageContainer.TFrame')
        
        # Bind events to update the scroll region when the interior frame changes size
        self.interior_frame.bind('<Configure>', lambda e: self.canvas.config(
            scrollregion=self.canvas.bbox("all")
        ))
        
        # Create a window on the canvas to hold the interior frame
        self.canvas.create_window((0, 0), window=self.interior_frame, anchor="nw")
        
        # --- Populate with Images ---
        self._populate_images()
        self._create_buttons()
        
        # Display selected item
        #ttk.Label(master, textvariable=self.selected_item).pack(pady=5)
        self.init_item_button.pack(pady=5)
    
    def _create_buttons(self):
        self.init_item_button = tk.Button(
            self.master,
            text = 'Add Item',
            width = 10,
            command = self.init_item_action,
            font = ('arial black', 10),
            bg = '#7F7F7F',
            borderwidth = 2,
            highlightcolor = '#CC8308',
            highlightthickness = 3,
            activebackground = '#ADADAD'
            )
    
    def init_item_action(self):
        pass
    
    def _populate_images(self):
       for i, path in enumerate(self.image_paths):
           try:
               # Load and resize the image (PIL/Pillow)
               img = Image.open(path)
               img = img.resize((296, 56), Image.LANCZOS) # Example banner size
               photo_image = ImageTk.PhotoImage(img)

               # Create a Label to hold the image (acting as the banner)
               # We use a Button style to easily show selection borders
               label = tk.Label(
                   self.interior_frame,
                   image=photo_image,
                   borderwidth=2,
                   relief="raised" # Use raised relief as default, sunken for selected
               )
               label.image = photo_image  # Keep a reference!
               
               # Use a lambda to handle the selection logic when clicked
               label.bind("<Button-1>", lambda e, item_name=Path(path).name, label=label: self._select_item(item_name, label))
               
               label.pack(fill='x', padx=5, pady=1)
               
           except FileNotFoundError:
               print(f"Image not found at: {path}")

    def _select_item(self, item_name, new_selected_label):
        """Handles visual and data selection."""
        
        # 1. Deselect the previously selected item (if one exists)
        for widget in self.interior_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(relief="raised", borderwidth=2)
                
        # 2. Select the new item visually
        new_selected_label.config(relief="sunken", borderwidth=2)
        
        # 3. Update the data variable
        self.selection_callback(item_name)
        self.selected_item.set(f"Selected: {item_name}")