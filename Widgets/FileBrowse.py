
from tkinter.ttk import *
import tkinter as tk
import os
from tkinter import filedialog

class FileBrowse(Frame):
    def __init__(self, window, file_text, path_text, ask_text, file_types, load_action=None):
        super().__init__(window)
        self.ask_text = ask_text
        self.load_action = load_action
        self.file_types = file_types
        self.file_path = tk.StringVar()
        self.file_path_frame = LabelFrame(self, text=file_text)
        self.file_path_frame.pack(side='top', expand=True, fill='x')
        
        self.file_path_label = Label(self.file_path_frame, text=path_text)
        self.file_path_label.pack(side='left', padx=5, pady=5)
        
        self.file_path_input = Entry(self.file_path_frame, textvariable=self.file_path)
        self.file_path_input.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        
        self.file_path_btn = Button(self.file_path_frame, text='Browse...', style='Buttons.TButton', command=self.file_browse)
        self.file_path_btn.pack(side='left', padx=5, pady=5)


    def file_browse(self):
        cur_path = os.getcwd()        
        temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, filetypes=[self.file_types], title=self.ask_text)
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        self.file_path.set(temp_path)
        self.load_action(self)
        return
    
    def get_path(self):
        return self.file_path.get()
    
    def set_controller(self, controller):
        self.controller = controller



if __name__=='__main__':
    root = tk.Tk()
    def load_action(*args):
        self = args[0]
        file_path = self.file_path.get()
        if len(file_path) > 0:
            with open(file_path, 'r') as f:                
                text = f.readline() 
                print(text)
                self.controller.test_label.config(text=text)
        return
    
    class Controller():
        def __init__(self, test_label):
            self.test_label = test_label    

    file_browse = FileBrowse(root, 'LT Grid File', 'Path', 'Please select a LT Grid File (*.txt)', ('LT Grid', '*.txt'), load_action=load_action)
    file_browse.pack(side='top')
    test_label = Label(root, text='Test Label')
    test_label.pack(side='top')
    controller = Controller(test_label)
    file_browse.set_controller(controller)        
    
    root.mainloop()