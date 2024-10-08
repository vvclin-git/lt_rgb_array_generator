import imp
import os
from tkinter import filedialog
from rgb_array_generator import gen_array, draw_pixel_frame, gen_LT_grid_fn, gen_lt_key_vars
import re
import time
import json
from tkinter.ttk import *
from Widgets import MsgBox
from Widgets import PresetFileLoad
from Widgets import PathBrowse
from Widgets import ParameterTab
from Widgets import FileBrowse
from PIL import Image, ImageTk
from Widgets.ZoomCanvas import *

from LightTools import LTAPIx
from LightTools.helpers import LT_Error

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

        self.load_paras_btn = Button(self.array_para_frame, text='Load', command=self.load_paras)
        self.load_paras_btn.pack(side='right', padx=2, pady=5)        

        # LT Link & RGB Array Application
        self.lt_error = LT_Error()
        self.loc = LTAPIx.LTLocator()
        self.lt = None
        self.lt_frame = LabelFrame(self.settings, text='LightTools')
        self.lt_frame.pack(side='top', expand=1, fill='x')
        self.lt_grid_file_load = FileBrowse(self.lt_frame, 'LT Grid File', 'Path', 'Please select a LT Grid File (*.txt)',('LT Grid', '*.txt'), load_action=self.preview_grid)
        self.lt_grid_file_load.pack(side='top', expand=1, fill='x')
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
        self.lt_grid_file_load.set_controller(self.controller)   

    def load_paras(self):
        cur_path = os.getcwd()        
        temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, filetypes=[('JSON File', '*.json')], title='Please select a JSON File (*.json)')
        with open(temp_path, 'r') as f:
            loaded_paras = json.load(f)
        self.array_para_tab.parameter_chg(loaded_paras)
        self.controller.msg_box.console(f'RGB Array Parameter File Loaded From: {temp_path}')
        return
    
    def preview(self):        
        array_paras = self.array_para_tab.output_parsed_vals()
        array_im, output_msg = self.gen_array(array_paras)
        preview_box_paras = [array_paras[0], array_paras[2], array_paras[3]]
        array_im = draw_pixel_frame(array_im, *preview_box_paras)
        array_im = cv2.cvtColor(array_im, cv2.COLOR_BGR2RGB)
        self.preview_canvas.update_im(array_im)
        self.controller.msg_box.console(output_msg)
        return
    # @staticmethod
    def preview_grid(self):
        lt_grid_fn = self.lt_grid_file_load.get_path()
        with open(lt_grid_fn, 'r') as f:
            lt_grid_header = f.readline()
        lt_grid_header = lt_grid_header.split(' ')
        grid_res = np.array(lt_grid_header[1:3], dtype='uint')
        grid_dim = np.array(lt_grid_header[3:], dtype='float')
        grid_dim = [grid_dim[2] - grid_dim[0], grid_dim[3] - grid_dim[1]]
        lt_grid_fn_list = lt_grid_fn.split('/')[-1]
        lt_grid_fn_list = lt_grid_fn_list.split('_')
        px_scale = lt_grid_fn_list[0].split(' ')[-1]
        px_size = lt_grid_fn_list[1]
        output_msg = f'''LT grid file loaded: {lt_grid_fn}
Grid File Resolution: {grid_res[0]}x{grid_res[1]}
Grid Dimension: {grid_dim[0]}x{grid_dim[1]} mm
Pixel Scale: {px_scale}
Pixel Size: {px_size} µm                        
                      '''
        self.controller.msg_box.console(output_msg)
        
        lt_grid_fns = { "R": f'{lt_grid_fn[0:-23]}R{lt_grid_fn[-22:]}',
                        "G": f'{lt_grid_fn[0:-23]}G{lt_grid_fn[-22:]}',
                        "B": f'{lt_grid_fn[0:-23]}B{lt_grid_fn[-22:]}' }        
        # check both key and grid file exist before applying grid file to surface
        lt_grid_list = []
        for c in ['R', 'G', 'B']:                      
            if not os.path.exists(lt_grid_fns[c]):
               self.controller.msg_box.console(f'Grid file not available for color {c}, abort')
               return  
            lt_grid_list.append(np.loadtxt(lt_grid_fns[c], skiprows=1))
        array_im = np.zeros([lt_grid_list[0].shape[0], lt_grid_list[0].shape[1], 3], dtype='uint8')
        array_im[:, :, 0] = lt_grid_list[0]
        array_im[:, :, 1] = lt_grid_list[1]
        array_im[:, :, 2] = lt_grid_list[2]
        array_im = cv2.cvtColor(array_im, cv2.COLOR_BGR2RGB)
        self.preview_canvas.update_im(array_im)

        return

    def lt_link(self):
        lt_paras = self.lt_link_para_tab.output_parsed_vals()
        pid = lt_paras[0]
        self.lt = self.loc.GetLTAPIFromPID(pid)
        if self.lt is not None:
            stat = self.lt.Message('Script LT connection established')        
            self.controller.msg_box.console(f'Connected to LT PID {pid}')
        else:            
            self.controller.msg_box.console(f'Failed to connect to LT PID {pid}')
        return
    
    def lt_set(self):
        if self.lt == None:
            self.controller.msg_box.console('No LT Connection')
            return
        
        lt_paras = self.lt_link_para_tab.output_parsed_vals()
        lt_source_key = lt_paras[1][0:-13]
        lt_source_keys = gen_lt_key_vars(lt_source_key)
        lt_grid_fn = self.lt_grid_file_load.get_path()
        lt_grid_fns = { "R": f'{lt_grid_fn[0:-23]}R{lt_grid_fn[-22:]}',
                        "G": f'{lt_grid_fn[0:-23]}G{lt_grid_fn[-22:]}',
                        "B": f'{lt_grid_fn[0:-23]}B{lt_grid_fn[-22:]}' }
        
        # check both key and grid file exist before applying grid file to surface
        for c in ['R', 'G', 'B']:
            _, stat = self.lt.DbGet(lt_source_keys[c], 'LoadFileName')
            if stat != 0:
               self.controller.msg_box.console(f'Invalid key detected for color {c}, abort')
               return                       
            if not os.path.exists(lt_grid_fns[c]):
               self.controller.msg_box.console(f'Grid file not available for color {c}, abort')
               return 

        for c in ['R', 'G', 'B']:
            stat = self.lt.DbSet(lt_source_keys[c], 'LoadFileName', lt_grid_fns[c].replace('/', '\\'))
            if stat != 1 and stat != 0:
                self.controller.msg_box.console(f'Error applying source grid for color: {c}')
            else:
                self.controller.msg_box.console(f'Applied {lt_grid_fns[c]} to source grid')
                
        return
    
    def gen_array(self, para_list):                
        array_im, output_msg = gen_array(*para_list)
        # chart_im, output_msg, _ = CHART_FN_DICT[chart_type](*para_list)
        return array_im, output_msg

    def output(self):        
        output_path = self.output_path.get_path()
        if len(output_path) == 0:
            self.controller.msg_box.console('No file output, output path not specified')
            return        
        timestr = time.strftime("%Y%m%d-%H-%M-%S")        
        array_paras = self.array_para_tab.output_parsed_vals()
        gen_lt_grid_paras = [*array_paras[0:4]]
        self.controller.msg_box.console(f'Output Path: {output_path}')        
        self.controller.msg_box.console(f'Generating RGB Pattern Files...')            
        array_im, output_msg = self.gen_array(array_paras)
        array_im = cv2.cvtColor(array_im, cv2.COLOR_BGR2RGB)
        self.preview_canvas.update_im(array_im)
        self.controller.msg_box.console(output_msg)
        header, output_fn = gen_LT_grid_fn(*gen_lt_grid_paras)
        for i, c in enumerate(['R', 'G', 'B']):             
            np.savetxt(f'{output_path}\\{output_fn}_{c}_{timestr}.txt', array_im[:, :, i], fmt='%d', delimiter=' ', header=header, comments='')
        self.controller.msg_box.console(f'Exporting {output_fn}_{timestr}.png...', cr=False)
        stat = cv2.imwrite(f'{output_path}\\{output_fn}_{timestr}.png', cv2.cvtColor(array_im, cv2.COLOR_RGB2BGR))
        if stat:
            self.controller.msg_box.console(f'Done', cr=True)
            self.lt_grid_file_load.file_path.set(f'{output_path}\\{output_fn}_{c}_{timestr}.txt')
            vals_dump = self.array_para_tab.dump_values()
            with open(f'{output_path}\\{output_fn}_{timestr}.json', 'w') as f:
                json.dump(vals_dump, f)
        else:
            self.controller.msg_box.console(f'Failed', cr=True)
        return
     

class Controller():
    def __init__(self, msg_box, preset_file_load, output_path, preview_canvas):
        self.msg_box = msg_box
        self.msg_box = msg_box
        self.preset_file_load = preset_file_load
        self.output_file_path = output_path        
        self.preview_canvas = preview_canvas