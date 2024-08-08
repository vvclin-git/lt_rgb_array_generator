import imp
import os
from tkinter import filedialog
import rgb_array_generator
import re
import time
import json
from tkinter.ttk import *
from Widgets import MsgBox
from Widgets import PresetFileLoad
from Widgets import PathBrowse
from Widgets import ParameterTab
from PIL import Image, ImageTk
from Widgets.ZoomCanvas import *


OUTPUT_PATH = f'{os.getcwd()}\\Output'
PRESET_PATH = f'{os.getcwd()}\\Presets\\parameters.json'

regex_coord = re.compile(r'\d+x\d+')
regex_color = re.compile(r'\d+,\d+,\d+')

class RGBGenerator(Frame):
    def __init__(self, window, preview_img_size):
        super().__init__(window)
        
        with open('.\\Presets\\parameters.json', 'r') as paras_json:
            # Load the content of the JSON file
            data = json.load(paras_json)
            
            # Extract the parameters
            array_paras = data['RGB_array_parameters']
            lt_paras = data['LT_parameters']

        self.preview_img_size = preview_img_size
        self.columnconfigure(0, weight=2, uniform=1)
        self.columnconfigure(1, weight=1, uniform=1)
        self.rowconfigure(0, weight=1, uniform=1)
        
        # Output container settings
        output = Frame(self, style='Output.TFrame', padding=(10, 10))   
        output.grid(row=0, column=0, sticky="NEWS")
        output.rowconfigure(0, weight=5, uniform=1)
        output.rowconfigure(1, weight=1, uniform=1)
        output.columnconfigure(0, weight=1)
        
        # Preview Image Widget
        img_width = self.preview_img_size[0]
        img_height = self.preview_img_size[1]                     
        preview_frame = LabelFrame(output, text='Preview Image', style='Test.TLabelframe')           
        preview_frame.grid(row=0, column=0, sticky='NEWS', pady=(0, 10))           
        
        img = np.zeros([img_height, img_width, 3], dtype=np.uint8)
        preview_img_text = f'Preview Image ({img_width} x {img_height})'
        
        preview_img_text_size = cv2.getTextSize(preview_img_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
        preview_img_text_pos = (int((img_width - preview_img_text_size[0][0]) * 0.5), int((img_height - preview_img_text_size[0][1]) * 0.5))        
        cv2.putText(img, preview_img_text, preview_img_text_pos, fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 0), fontScale=1, thickness=1)        
        
        self.preview_img = Image.fromarray(img)        
        self.preview_canvas = Zoom_Advanced(preview_frame, self.preview_img)             

        # Message Output     
        msg_frame = LabelFrame(output, text='Output Message', style='TLabelframe')  
        msg_frame.grid(row=1, column=0, sticky='NEWS')
        self.msg_box = MsgBox(msg_frame)        
        self.msg_box.pack(side='top', expand=1, fill='both')        
        
        # Settings Container Settings        
        self.settings = Frame(self, style='Settings.TFrame', padding=(10, 10))        
        self.settings.grid(row=0, column=1, sticky='NEW')
                
        # Preset Save / Load
        self.preset_file_load = PresetFileLoad(self.settings)
        self.preset_file_load.pack(side='top', expand=1, fill='x')
        
        # Output Path
        self.output_path = PathBrowse(self.settings)
        self.output_path.pack(side='top', expand=1, fill='x', pady=5)

        # Array Parameter Setting
        self.array_para_frame = LabelFrame(self.settings, text='RGB Array Parameters')
        self.array_para_frame.pack(side='top', expand=1, fill='x', pady=5)
        self.array_para_tab = ParameterTab(self.array_para_frame, array_paras)        
        self.array_para_tab.pack(side='top', expand=1, fill='x', pady=5, padx=2)
                
        self.output_btn = Button(self.array_para_frame, text='Output', command=self.output)
        self.output_btn.pack(side='right', padx=2, pady=5)        
        
        self.preview_btn = Button(self.array_para_frame, text='Preview', command=self.preview)
        self.preview_btn.pack(side='right', padx=2, pady=5)

        # LT Link & RGB Array Application
        self.lt_frame = LabelFrame(self.settings, text='LightTools')
        self.lt_frame.pack(side='top', expand=1, fill='x')
        self.lt_link_para_tab = ParameterTab(self.lt_frame, lt_paras)
        self.lt_link_para_tab.pack(side='top', expand=1, fill='x', pady=5, padx=2)
        self.lt_set_btn = Button(self.lt_frame, text='Set RGB Array', command=self.lt_set)
        self.lt_set_btn.pack(side='right', padx=2, pady=5)   
        self.lt_link_btn = Button(self.lt_frame, text='Link LT', command=self.lt_link)
        self.lt_link_btn.pack(side='right', padx=2, pady=5)       
        
        # Widget Initialization
        self.controller = Controller(self.msg_box, self.preset_file_load, self.output_path, self.preview_canvas)

        linked_tabs = {'RGB_array_parameters':self.array_para_tab, 'LT_parameters':self.lt_link_para_tab}

        self.preset_file_load.init_linked_tabs(linked_tabs)
        self.preset_file_load.preset_path.set(PRESET_PATH)
        self.preset_file_load.load_preset()
        self.preset_file_load.set_controller(self.controller)   

    def preview(self):        
        array_paras = self.array_para_tab.output_parsed_vals()
        array_im, output_msg = self.gen_array(array_paras)
        self.preview_canvas.update_im(chart_im)
        self.controller.msg_box.console(output_msg)
        return
    
    def lt_link(self):
        return
    def lt_set(self):
        return
    def gen_array(self, para_list):                
        
        # chart_im, output_msg, _ = CHART_FN_DICT[chart_type](*para_list)        
        return chart_im, output_msg

    def output(self):        
        output_path = self.output_path.get_path()
        if len(output_path) == 0:
            self.controller.msg_box.console('No file output, output path not specified')
            return
        output_name = ''
        timestr = time.strftime("%Y%m%d-%H-%M-%S")
        
        array_paras, variant = self.array_para_tree.output_parsed_vals(preview=False)
        self.controller.msg_box.console(f'Output Path: {output_path}')
        for t in array_paras:
            self.controller.msg_box.console(f'Generating {t}...')
            if variant:
            # if type(array_paras[t]) == list:
                for v in array_paras[t]:
                    chart_im, output_msg = self.gen_chart(t, v)
                    output_name = self.gen_output_name(output_msg)
                    self.controller.msg_box.console(f'Exporting {output_name}{timestr}.png...', cr=False)
                    stat = cv2.imwrite(f'{output_path}\\{output_name}{timestr}.png', chart_im)
                    if stat:
                        self.controller.msg_box.console(f'Done', cr=True)        
                    else:
                        self.controller.msg_box.console(f'Failed', cr=True)
            else:
                chart_im, output_msg = self.gen_chart(t, array_paras[t])
                output_name = self.gen_output_name(output_msg)
                self.controller.msg_box.console(f'Exporting {output_name}{timestr}.png...', cr=False)
                stat = cv2.imwrite(f'{output_path}\\{output_name}{timestr}.png', chart_im)
                if stat:
                    self.controller.msg_box.console(f'Done', cr=True)        
                else:
                    self.controller.msg_box.console(f'Failed', cr=True)
        return

    def gen_output_name(self, chart_output_msg):
        out_paras = chart_output_msg.replace('\n', ',').split(',')        
        out_paras_dict = {}
        for i in range(len(out_paras) - 1):
            p = out_paras[i]
            para = p.split(':')
            out_paras_dict[para[0]] = para[1].lstrip()        
        output_name = ''
        for p in out_paras_dict:
            if p in {'Chart Type', 'Resolution', 'Grid Dimension', 'Grille Size', 'Padding'}:
                output_name += f'{out_paras_dict[p]}_'        
        return output_name        

class Controller():
    def __init__(self, msg_box, preset_file_load, output_path, preview_canvas):
        self.msg_box = msg_box
        self.msg_box = msg_box
        self.preset_file_load = preset_file_load
        self.output_file_path = output_path
        
        self.preview_canvas = preview_canvas