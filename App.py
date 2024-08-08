import tkinter as tk
from tkinter import ttk
from tkinter.constants import CENTER
from tkinter.ttk import *
from Frames import RGBGenerator
from windows import set_dpi_awareness
from tkinter import filedialog
import time

set_dpi_awareness()

# Color Palette Definition
COLOUR_PRIMARY = "#2e3f4f"
COLOUR_SECONDARY = "#293846"
COLOUR_LIGHT_BACKGROUND = "#fff"
COLOUR_LIGHT_TEXT = "#eee"
COLOUR_DARK_TEXT = "#8095a8"

class LT_RGB_Array_Gen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('LT RGB Array Generator')
        self.geometry('1480x990')
        preview_img_size = (960, 740)
        
        # self.geometry('1680x990')
        # self.resizable(width=False, height=False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)                
        
        
        # Styling
        style = Style()
        style.theme_use('clam')
        
        style.configure('Red.TFrame', background='red')
        style.configure('Green.TFrame', background='green')
        style.configure('Blue.TFrame', background='blue')
        
        
        style.configure('Output.TFrame', background='red')
        style.configure('Settings.TFrame', background='green')
        style.configure('Buttons.TFrame', background='blue')                        
        style.configure('TLabelframe', relief='groove', borderwidth=2)
        style.configure('Test.TLabelframe', relief='groove', borderwidth=2, background='green')
        style.configure("Treeview.Heading", background="#ededed", foreground="black", relief='flat', bordercolor='black', borderwidth=2)
        style.configure('Treeview', bordercolor='black', borderwidth=2)
        style.configure('Buttons.TButton')
        style.configure('PathEntry.TEntry', ipad=5)
        style.configure('TestLabel1.TLabel', background='red')
        style.configure('TestLabel2.TLabel', background='green')
        style.configure('TestLabel3.TLabel', background='blue')
        
        container = Frame(self)        
        container.grid(row=0, column=0, sticky='NSEW')
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        
        tab_control = ttk.Notebook(container)
        tab_test_charts = RGBGenerator(tab_control, preview_img_size)        
        
        tab_control.add(tab_test_charts, text='RGB Array Generator')
             
        tab_control.pack(expand=1, fill='both')


    # def show_frame(self, container):
    #     frame = self.frames[container]
    #     frame.tkraise()

root = LT_RGB_Array_Gen()
root.mainloop()