
import tkinter as tk
from tkinter import Button, Entry, ttk
import re
from typing import Text

import cv2
from tkinter import messagebox


class ParameterTab(ttk.Frame):
    def __init__(self, parent, parameters):
        super().__init__(parent)
        self.parameters = parameters     
        self.tree = ttk.Treeview(self, show='headings', columns=("1", "2"))
        self.tree['show'] = 'headings'

        self.tree.column("1")
        self.tree.heading("1", text="Parameter")
        self.tree.column("2")
        self.tree.heading("2", text="Value")
        
        for p in self.parameters:            
            self.tree.insert("", "end", values=(p, self.parameters[p]['value']), tags=self.parameters[p]['type'])              
        
        self.tree.tag_bind('value', '<1>', self.val_edit)
        self.tree.tag_bind('list', '<1>', self.list_edit)
        self.tree.pack(fill='x', expand=True)        
    
    def val_edit(self, event): # value edit event handler
        if self.tree.identify_region(event.x, event.y) == 'cell':
            # the user clicked on a cell
            column = self.tree.identify_column(event.x)  # identify column
            item = self.tree.identify_row(event.y)  # identify item                
            # print(self.tree.item(item)['tags'])
            print(item)
            if column == '#2': # only value column is allowed for editing
                x, y, width, height = self.tree.bbox(item, column) 
                value = self.tree.set(item, column)
                
                def ok(event):
                    """Change item value."""
                    para_name = self.tree.set(item, '#1')
                    regex = re.compile(eval(self.parameters[para_name]['regex']))
                    if regex.search(entry.get()):
                        self.tree.set(item, column, entry.get())
                        entry.destroy()
                    else:
                        messagebox.showinfo('Input Validation', 'Wrong input format!')
                        return

            else:
                return
        else:
            return
        # display the Entry   
        entry = ttk.Entry(self.tree)  # create edition entry
        entry.place(x=x, y=y, width=width, height=height, anchor='nw')  # display entry on top of cell
        entry.insert(0, value)  # put former value in entry
        entry.bind('<FocusOut>', lambda e: entry.destroy())  
        entry.bind('<Return>', ok)  # validate with Enter
        entry.focus_set()

    def list_edit(self, event): # drop-down list edit event handler
        if self.tree.identify_region(event.x, event.y) == 'cell':
            # the user clicked on a cell
            column = self.tree.identify_column(event.x)  # identify column
            item = self.tree.identify_row(event.y)  # identify item                
            # print(self.tree.item(item)['tags'])
            if column == '#2':
                x, y, width, height = self.tree.bbox(item, column) 
                value = self.tree.set(item, column)
                para_name = self.tree.set(item, '#1')
                options = self.parameters[para_name]['options']
                def ok(event, dummy_1, dummy_2):
                    """Change item value."""
                    self.tree.set(item, column, val.get())
                    val_list.destroy()
            else:
                return
        else:
            return
        # display the drop-down list   
        val = tk.StringVar()
        val_list = ttk.OptionMenu(self.tree, val, options[0], *options)  # create drop-down list
        val_list.place(x=x, y=y, width=width, height=height, anchor='nw')  # display drop-down on top of cell
        val.set(value)  # put former value in entry
        val_list.bind('<FocusOut>', lambda e: val_list.destroy())              
        val.trace('w', ok) # drop-down list value change event 
        val_list.focus_set()

    def output_values(self):
        output = []
        for p in self.tree.get_children():
            output.append(self.tree.item(p)['values'])
        return output
    
    def output_parsed_vals(self):
        output_vals = self.output_values()
        parsed_paras = []
        for r in output_vals:
            para_name = r[0]
            val = str(r[1])
            parser = self.parameters[para_name]['parser']            
            if len(val.split(',')) > 1:
                parsed = self.list_parser(val, parser)
            else:
                if parser:
                    parsed = eval(parser)
                else:
                    parsed = val
            parsed_paras.append(parsed)
        return parsed_paras


    def list_parser(self, in_str, parser):
        output = []
        in_str_list = in_str.split(',')
        for val in in_str_list:
            if parser:
                parsed = eval(parser)
            else:
                parsed = val
            output.append(parsed)
        return output

    def clear(self):
        self.tree.delete(*self.tree.get_children())
        return
    
    def submit_value(self, parameter, value):        
        for p in self.tree.get_children():
            if self.tree.item(p)['values'][0] == parameter:
                # print(self.tree.item(p))
                regex = re.compile(eval(self.parameters[parameter]['regex']))
                if regex.search(value):                    
                    self.tree.set(p, '#2', value)
                else:
                    raise TypeError('Incorrect data format')
        return
    
    def parameter_chg(self, selected_parameters):
        self.clear()
        self.parameters = selected_parameters
        for p in selected_parameters:
            # print(p)            
            self.tree.insert("", "end", values=(p, selected_parameters[p]['value']), tags=selected_parameters[p]['type'])
        return

    def fit_height(self):
        height = len(self.parameters)
        self.tree.configure(height=height)
        return

if __name__ == '__main__':
    root = tk.Tk()
    # parameters = {'Parameter 1': {'value':1, 'type':'value', 'options':None},
    #               'Parameter 2': {'value':2, 'type':'value', 'options':None},
    #               'Parameter 3': {'value':'cv2.FILLED', 'type':'list', 'options':('cv2.FILLED', 'cv2.LINE_4', 'cv2.LINE_8', 'cv2.LINE_AA')},
    #               'Parameter 4': {'value':'e', 'type':'list', 'options':('e', 'f', 'g')},
    #               'Parameter 5': {'value':0.001, 'type':'value', 'options':None}}
    
    parameters = {'Parameter 1': {'value':'10x10', 'type':'value', 'regex':"r'^\\d+x\\d+$'", 'parser':"(int(val.split('x')[0]), int(val.split('x')[1]))", 'options':None},
                  'Parameter 2': {'value':'5.5x5.5', 'type':'value', 'regex':"r'^\\d+.\\d+x\\d+.\\d+$'", 'parser':"(float(val.split('x')[0]), float(val.split('x')[1]))", 'options':None},
                  'Parameter 3': {'value':'cv2.FILLED', 'type':'list', 'regex':"r'^cv2?[.]'", 'parser':'eval(val)', 'options':('cv2.FILLED', 'cv2.LINE_4', 'cv2.LINE_8', 'cv2.LINE_AA')},
                  'Parameter 4': {'value':'e', 'type':'list', 'regex':None, 'parser':None, 'options':('e', 'f', 'g')},
                  'Parameter 5': {'value':0.001, 'type':'value','regex':"r'^[-]*\d+[.]\d+$'", 'parser':'float(val)', 'options':None},
                  'Parameter 6': {'value':1, 'type':'value','regex':"r'^[1-9]\d*$'", 'parser':'int(val)', 'options':None},
                  'Parameter 7': {'value':-1, 'type':'value','regex':"r'^[-]*[1-9]\d*$'", 'parser':'int(val)', 'options':None}}

    para_tab = ParameterTab(root, parameters)
    para_tab.pack()
        
    def print_parsed_vals():
        parsed = para_tab.output_parsed_vals()
        for v in parsed:
            print(f'Type: {type(v)}, Value: {v}')
    
    def submit_val_test():
        parameter = para_input.get()
        value = val_input.get()
        para_tab.submit_value(parameter, value)

    parse_test_btn = Button(root, text='Print Parsed Values', command=print_parsed_vals)
    parse_test_btn.pack()
    
    submit_test_btn = Button(root, text='Submit Test', command=submit_val_test)
    submit_test_btn.pack()

    para_input = Entry(root)
    para_input.pack()
    val_input = Entry(root)
    val_input.pack()
    
    root.mainloop()