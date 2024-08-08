
from tkinter.ttk import *
import tkinter as tk

class ToggleBtn(Button):
    def __init__(self, parent, on_txt, off_txt, on_cmd, off_cmd):
        super().__init__(parent)
        self.toggle_stat = False
        self.on_cmd = on_cmd
        self.off_cmd = off_cmd
        self.on_txt = on_txt
        self.off_txt = off_txt
        self.configure(command=self.toggle)
        self.configure(text=self.off_txt)
    
    def toggle(self):
        if not self.toggle_stat:
            self.on_cmd()
            self.toggle_stat = True
            self.configure(text=self.on_txt)
        else:
            self.off_cmd()
            self.toggle_stat = False
            self.configure(text=self.off_txt)
        return
        
if __name__=='__main__':
    on_txt = 'toggle on'
    off_txt = 'toggle off'

    def on_cmd():
        print('toggled on')
        return

    def off_cmd():
        print('toggled off')
        return

    root = tk.Tk()

    toggle_btn = ToggleBtn(root, on_txt, off_txt, on_cmd, off_cmd)
    toggle_btn.pack()

    root.mainloop()