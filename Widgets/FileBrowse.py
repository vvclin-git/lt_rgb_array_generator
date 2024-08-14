
from tkinter.ttk import *
import tkinter as tk
import os
from tkinter import filedialog

class FileBrowse(Frame):
    def __init__(self, window, file_text, path_text, ask_text):
        super().__init__(window)
        self.ask_text = ask_text
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
        temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, filetypes=[('LT Grid', '*.txt')], title=self.ask_text)
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        self.file_path.set(temp_path)
        return
    
    def get_path(self):
        return self.file_path.get()

if __name__=='__main__':
    root = tk.Tk()
    file_browse = FileBrowse(root, 'LT Grid File', 'Path', 'Please select a LT Grid File (*.txt)')
    file_browse.pack()
    root.mainloop()