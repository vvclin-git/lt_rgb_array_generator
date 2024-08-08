
import tkinter as tk
from tkinter.ttk import *


class MsgBox(Frame):
    def __init__(self, window):
        super().__init__(window)
        
        msg_frame = Frame(self)
        msg_frame.pack(side='top', expand=1, fill='both')

            
        self.msg_output = tk.Text(msg_frame, height=10, state='disabled')
        self.msg_output.pack(side=tk.LEFT, expand=True, fill='both')
        msg_scroll = Scrollbar(msg_frame, orient=tk.VERTICAL, command=self.msg_output.yview)
        self.msg_output['yscrollcommand'] = msg_scroll.set
        msg_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def console(self, msg, cr=True):
        self.msg_output.config(state='normal')
        if cr:
            self.msg_output.insert('end', msg + '\n')
            self.msg_output.see('end')
        else:
            self.msg_output.insert('end', msg)
        self.msg_output.config(state='disabled')
        return
    
    def console_clr(self):
        self.msg_output.config(state='normal')
        self.msg_output.delete('1.0', 'end')
        self.msg_output.config(state='disabled')

    def console_update(self, msg):
        self.msg_output.config(state='normal')
        self.msg_output.delete("end-1c linestart", 'end-1c lineend')
        self.msg_output.insert("end-1c linestart", msg)
        self.msg_output.config(state='disabled')
        self.msg_output.update()

if __name__=='__main__':
    root = tk.Tk()
    msg_box = MsgBox(root)
    msg_box.pack()
    
    

    def test():
        msg_box.console('test')

    def clr_test():
        msg_box.console_clr()

    counter = 0
    def upd_test():
        global counter 
        counter += 1
        msg_box.console_update(f'{counter}')

    test_btn = Button(root, text='test', command=test)
    test_btn.pack()

    clr_btn = Button(root, text='clear', command=clr_test)
    clr_btn.pack()

    upd_btn = Button(root, text='update', command=upd_test)
    upd_btn.pack()

    root.mainloop()