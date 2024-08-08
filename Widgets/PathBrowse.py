
import cv2
import numpy as np
from tkinter.ttk import *
import tkinter as tk
from PIL import Image, ImageTk

import os
import json
from tkinter import filedialog

class PathBrowse(Frame):
    def __init__(self, window):
        super().__init__(window)
        
        self.output_path = tk.StringVar()
        self.output_path_frame = LabelFrame(self, text='Path Browse')
        self.output_path_frame.pack(side='top', expand=True, fill='x')
        
        self.output_path_label = Label(self.output_path_frame, text='Output Path')
        self.output_path_label.pack(side='left', padx=5, pady=5)
        
        self.output_path_input = Entry(self.output_path_frame, textvariable=self.output_path)
        self.output_path_input.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        
        self.output_path_btn = Button(self.output_path_frame, text='Browse...', style='Buttons.TButton', command=self.path_browse)
        self.output_path_btn.pack(side='left', padx=5, pady=5)


    def path_browse(self):
        cur_path = os.getcwd()
        temp_path = filedialog.askdirectory(parent=self, initialdir=cur_path, title='Please select a directory')
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        if len(temp_path) > 0:
            self.output_path.set(temp_path + '/')
        return
    
    def get_path(self):
        return self.output_path.get()

if __name__=='__main__':
    root = tk.Tk()
    path_browse = PathBrowse(root)
    path_browse.pack()
    root.mainloop()