import tkinter as tk
from PIL import ImageTk, Image
from pathlib import Path
import ast
import threading

from utils.logger import logger as log
from utils.ui_utils.styles import load_styles
from utils.ui_utils.apps import ImageListApp
from utils.dependents import format_funcs
import utils.dependents.json_handler as json_handler


MODULE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = MODULE_DIR / 'utils' / "media" / "main3.png"

class UIManager:
    """Encapsulates all GUI logic, built upon a single root window."""

    def __init__(self, master, bot_start_callback, stop_signal):
        self.root = master
        
        self.bot_start_callback = bot_start_callback
        self.stop_signal = stop_signal
        
        self.selectedItemData = None
        self.exit_script = False
        
        self._build_ui()
        
        self.image_container_frame = self.entryframe
        
        
    def get_image_container(self):
        return self.image_container_frame
        
    def _build_ui(self):
        self.root.title("Dadbot")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.img = ImageTk.PhotoImage(Image.open(IMAGE_PATH))

        self.mainframe = tk.Canvas(self.root, borderwidth=2, relief='solid')
        self.mainframe.grid(sticky=tk.N + tk.E + tk.S + tk.W)
        self.mainframe.create_image(0, 0, image=self.img, anchor=tk.NW)

        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        
        self.entryframe = tk.Frame(self.mainframe, borderwidth=8, relief='raised', background='#1F232D')

        self.entryframe.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S, padx=20, pady=20)
        self.entryframe.columnconfigure(0, weight=1)
        self.entryframe.columnconfigure(1, weight=1)
        
        for i in range(2):
            self.entryframe.rowconfigure(i, weight=1)

        self._create_buttons()
        
        self.start_button.grid(row=0, column=2, padx=25, pady=25)
        self.exit_button.grid(row=0, column=1, padx=25, pady=25)
        
    def _create_buttons(self):
        
        self.start_button = tk.Button(
            self.mainframe, 
            text='Start', 
            width=10,
            command=self.start_button_action,
            font=('arial black', 12), 
            bg='#7F7F7F',
            relief='raised',
            borderwidth=4,
            highlightcolor='#CCB30B',
            highlightthickness=3,
            activebackground='#ADADAD'
        )


        self.exit_button = tk.Button(
            self.mainframe,
            text='Exit', 
            width=10,
            command=self.exit_button_action,
            font=('arial black', 12), 
            bg='#7F7F7F',
            relief='raised',
            borderwidth=4,
            highlightcolor='#CCB30B',
            highlightthickness=3,
            activebackground='#ADADAD'
        )
        
    def format_for_json(self):
        formattedName = format_funcs.format_item_for_img_loc(
            self.selectedItemData[0],
            self.selectedItemData[1]
            )
        return formattedName
    
    def set_item_exists(self):
        formattedName = self.format_for_json()
        if self.selectedItemData is not None:
            self.itemExists = json_handler.item_check(formattedName)
        else:
            log.warning("Must select an item to continue.")
    
    def get_item_data(self):
        formattedName = self.format_for_json()
        
        itemData = json_handler.get_item_data(formattedName)
        
        # returns dimension, is_gold_storage, is_stackable, max_stack
        log.debug(f"json_handler gave {itemData}")
        return itemData
    
    def _start_bot_process(self):
        if self.selectedItemData is None:
            log.warning("Please select an item first.")
            return
        
        log.notice("Starting bot process... ")
        
        if self.itemExists:
            self.start_button.config(state = 'disabled')
            self.stop_signal.stop = False
            dim, is_gold_storage, is_stackable, max_stack = self.get_item_data()
            
        else:
            log.error(f"Selected item has not been initialized.")
            return
        
        
        # Adjustment metrics, mostly for new items.
        args_for_bot = {
            "item": self.selectedItemData[0],
            "rarity": self.selectedItemData[1],
            "previous_item": None,
            "amounts": [0, 0, 0, 720],
            "balAdjItem": "Centaur Tail",
            "balAdjItemLow": "Ale",
            "priceCatBypass": False,
            "dim": dim,
            "is_gold_storage": is_gold_storage,
            "is_stackable": is_stackable,
            "max_stack": max_stack,
            "stop_signal": self.stop_signal,
            "hasItem": True,
            "itemExists": self.itemExists
        }
        
        bot_thread = threading.Thread(
            target=self.bot_start_callback,
            kwargs=args_for_bot
            )
        
        bot_thread.start()
        
    def start_button_action(self):

        self._start_bot_process()
        
    def exit_button_action(self):
        self.exit_script = True
        
        self.stop_signal.stop = True
        log.notice("Exiting... ")
        self.root.destroy() 
        
    def run_ui(self):
        self.root.mainloop()
        
        if self.exit_script:
            return None
        
        return self.return_values
    
    def handle_banner_selection(self, selected_item_name):
        img_name = selected_item_name
        self.selectedItemData = format_funcs.format_item_from_img_loc(img_name)
        self.set_item_exists()
        print(f"Item exists: {self.itemExists}")
        print(f"Selected Item: {self.selectedItemData}")
    
def get_images_in_path():
    current_dir = Path(__file__).parent
    target_dir = current_dir / r'utils\actors\banner_images'
    banners = list(target_dir.glob('*.png'))
    
    return banners, target_dir

def start_ui(root, bot_start_callback, stop_signal):
    vals = get_images_in_path()
    banners = vals[0]
    json_handler.path_check()
    
    if banners:        
        load_styles(root)
        
        ui = UIManager(root, bot_start_callback, stop_signal)
        app_master_frame = ui.get_image_container()
        
        app = ImageListApp(app_master_frame, banners, 
                           selection_callback = ui.handle_banner_selection)
        
        root.mainloop()
        
    else:
        log.error(f"No images found in {vals[1]}")
        
if __name__ == '__main__':
    root = tk.Tk()
    start_ui(root)