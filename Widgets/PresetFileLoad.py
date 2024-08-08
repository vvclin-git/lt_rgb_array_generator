import cv2
import numpy as np
from tkinter.ttk import *
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import os
import json
from tkinter import filedialog

from Widgets.ChartParaTree import ChartParaTree
from Widgets.ParameterTab import ParameterTab

class PresetFileLoad(Frame):
    def __init__(self, window):
        super().__init__(window)
        
        self.controller = None
        self.preset_path = tk.StringVar()
        self.presets = {}
        self.linked_tabs = {}        
        
        self.preset_frame = LabelFrame(self, text='Parameter Preset')
        self.preset_frame.pack(expand=True, fill='x', side='top')

        self.preset_input_frame = Frame(self.preset_frame)
        self.preset_input_frame.pack(side='top', expand=True, fill='both')
        self.preset_btn_frame = Frame(self.preset_frame)
        self.preset_btn_frame.pack(side='top', expand=True, fill='both')

        self.preset_path_label = Label(self.preset_input_frame, text='Preset Path')
        self.preset_path_label.pack(side='left', padx=5, pady=5)
        self.preset_path_input = Entry(self.preset_input_frame, textvariable=self.preset_path)
        self.preset_path_input.pack(side='left', padx=5, pady=5, expand=True, fill='both')
        
        self.preset_save_btn = Button(self.preset_btn_frame, text='Save As...', style='Buttons.TButton', command=self.save_preset)        
        self.preset_save_btn.pack(side='right', padx=2, pady=5)
        self.preset_load_btn = Button(self.preset_btn_frame, text='Load...', style='Buttons.TButton', command=self.load_preset)
        self.preset_load_btn.pack(side='right', padx=2, pady=5)
        self.preset_browse_btn = Button(self.preset_btn_frame, text='Browse...', style='Buttons.TButton', command=self.browse_preset)
        self.preset_browse_btn.pack(side='right', padx=2, pady=5)
    
    def load_preset(self):
        f = open(self.preset_path.get(), 'r')
        self.presets = json.load(f)
        f.close()
        if self.controller:
            self.controller.msg_box.console(f'Preset File: {self.preset_path.get()} Loaded')
        for k in self.presets:
            if k in self.linked_tabs.keys():
                if type(self.linked_tabs[k]) == ParameterTab:
                    self.linked_tabs[k].parameter_chg(self.presets[k])
                    self.linked_tabs[k].fit_height()
                elif type(self.linked_tabs[k]) == ChartParaTree:
                    self.linked_tabs[k].parameter_chg(self.presets)
        return
    
    def save_preset(self):
        preset_path = self.preset_path.get()
        if os.path.isfile(preset_path):
            chk_overwrite = messagebox.askquestion(title='Confirm Overwrite', message='File already exists, overwrite?')
            if not chk_overwrite:
                return                
        f = open(preset_path, 'w')
        
        for k in self.linked_tabs:
            if type(self.linked_tabs[k]) == ParameterTab:
                for p in self.linked_tabs[k].output_values():
                    self.presets[k][p[0]]['value'] = p[1]
            elif type(self.linked_tabs[k]) == ChartParaTree:
                para_out = self.linked_tabs[k].output_values()
                for t in para_out:
                    for p in para_out[t]:                        
                        self.presets[k][t][p]['value'] = para_out[t][p]

        
        save_preset = self.presets
        json.dump(save_preset, f)
        f.close()
        if self.controller:
            self.controller.msg_box.console(f'Preset File: {preset_path} Saved')
        return

    def browse_preset(self):
        cur_path = os.getcwd()
        temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, title='Please select a JSON file', filetypes=[("JSON files","*.json")])
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        if len(temp_path) > 0:            
            self.preset_path.set(temp_path)
        return
    
    def init_linked_tabs(self, linked_tabs):
        self.linked_tabs = linked_tabs
        for k in self.linked_tabs:
            if type(self.linked_tabs[k]) == ParameterTab:
                self.presets[k] = linked_tabs[k].parameters
            elif type(self.linked_tabs[k]) == ChartParaTree:
                self.presets[k] = linked_tabs[k].tree_paras
            
    
    def set_controller(self, controller):
        self.controller = controller
       


if __name__=='__main__':
    from ParameterTab import ParameterTab
    para_1 = {'Parameter 1': {'value':1, 'type':'value', 'options':None},
              'Parameter 2': {'value':2, 'type':'value', 'options':None},
              'Parameter 3': {'value':'c', 'type':'list', 'options':('a', 'b', 'c')}
              }

    para_2 = {'Parameter 4': {'value':4, 'type':'value', 'options':None},
              'Parameter 5': {'value':5, 'type':'value', 'options':None},
              'Parameter 6': {'value':'f', 'type':'list', 'options':('d', 'e', 'f')}
             }
    presets = {'para_1':para_1, 'para_2':para_2}
        
    root = tk.Tk()
    paratab_1 = ParameterTab(root, presets['para_1'])
    paratab_1.pack(side='top')
    paratab_2 = ParameterTab(root, presets['para_2'])
    paratab_2.pack(side='top')
    load_preset = PresetFileLoad(root)
    load_preset.pack(side='top')
    linked_tabs = {'para_1':paratab_1, 'para_2':paratab_2}
    load_preset.init_linked_tabs(linked_tabs)
    root.mainloop()