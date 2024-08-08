import cv2
import numpy as np
from tkinter.ttk import *
import tkinter as tk
from PIL import Image, ImageTk

import os
import json
from tkinter import filedialog
from functools import partial

class ImgFileLoad(Frame):
    def __init__(self, window, load_func) -> None:
        super().__init__(window)
        self.im = None
        self.img_path = tk.StringVar()        

        self.img_load_frame = LabelFrame(window, text='Image Loading')
        self.img_load_frame.pack(expand=True, fill='x', side='top')
        
        self.img_load_input_frame = Frame(self.img_load_frame)
        self.img_load_input_frame.pack(side='top', expand=True, fill='both')
        self.img_load_btn_frame = Frame(self.img_load_frame)
        self.img_load_btn_frame.pack(side='top', expand=True, fill='both')
        
        self.img_path_label = Label(self.img_load_input_frame, text='Image Path')
        self.img_path_label.pack(side='left', padx=5, pady=5)
        self.img_path_input = Entry(self.img_load_input_frame, textvariable=self.img_path)        
        self.img_path_input.pack(side='left', expand=True, fill='x', padx=5, pady=5)

        img_load_btn = Button(self.img_load_btn_frame, text='Load', style='Buttons.TButton', command=partial(self.img_load, load_func))
        img_load_btn.pack(side='right', padx=2, pady=5)
        img_browse_btn = Button(self.img_load_btn_frame, text='Browse...', style='Buttons.TButton', command=self.img_browse)        
        img_browse_btn.pack(side='right', padx=2, pady=5)
    
    def img_browse(self):
        cur_path = os.getcwd()
        temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, title='Please select a image file', filetypes=[("PNG","*.png"), ("bmp","*.bmp"), ("JPG","*.jpg")])
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        if len(temp_path) > 0:            
            self.img_path.set(temp_path)
        return

    def img_load(self, load_func):
        img_path = self.img_path.get()
        if len(img_path) > 0:
            self.im = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            load_func()
        return
