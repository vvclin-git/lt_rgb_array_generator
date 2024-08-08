

import tkinter as tk
from tkinter.ttk import *
import json
import re
import cv2
from tkinter import messagebox


class ChartParaTree(Frame):
    def __init__(self, parent, tree_paras):
        super().__init__(parent)
        
        # self.parameters = parameters
        self.tree_paras = tree_paras
        self.chart_types = self.tree_paras['chart_types']
        self.chart_parameters = self.tree_paras['chart_parameters']
        self.chart_chk_paras = self.tree_paras['chart_chk_paras']
        
        self.tree = Treeview(self)
        self.tree.pack(expand=1, fill='both')        
        self.tree['columns'] = ('Value', 'Export')
                
        self.tree.column('Value', anchor=tk.W, width=100)
        self.tree.column('Export', anchor=tk.W, width=50)
        self.tree.heading('#0', text='Parameter', anchor=tk.W)
        self.tree.heading('Value', text='Values', anchor=tk.W)
        self.tree.heading('Export', text='Export', anchor=tk.W)

        self.tree.tag_bind('value', '<1>', self.val_edit)
        self.tree.tag_bind('list', '<1>', self.list_edit)
        self.tree.bind('<ButtonRelease-1>', self.get_selected_chart)
        self.selected_chart = ''
        
        for i, t in enumerate(self.chart_types):
            self.tree.insert('', tk.END, text=t, value=('', self.chart_chk_paras[t]['value']), tags=self.chart_chk_paras[t]['type'], iid=t, open=False)
            for j, k in enumerate(self.chart_parameters[t].keys()):
                self.tree.insert(t, tk.END, text=k, value=self.chart_parameters[t][k]['value'], tags=self.chart_parameters[t][k]['type'], iid=f'{t}_{k}', open=False)

    def get_selected_chart(self, event):
        curItem = self.tree.focus()
        if self.tree.parent(curItem) == '':
            self.selected_chart = curItem
        else:
            self.selected_chart = self.tree.parent(curItem)            
        return
    
    def val_edit(self, event): # value edit event handler
        if self.tree.identify_region(event.x, event.y) == 'cell':
            # the user clicked on a cell
            column = self.tree.identify_column(event.x)  # identify column
            item = self.tree.identify_row(event.y)  # identify item                
            # print(self.tree.item(item)['tags'])
            if column == '#1': # only value column is allowed for editing
                x, y, width, height = self.tree.bbox(item, column) 
                value = self.tree.set(item, column)
                
                def ok(event):
                    """Change item value."""
                    # para_name = self.tree.set(item, '#1')
                    chart_type = item.split('_')[0]
                    para_name = item.split('_')[1]
                    regex = re.compile(eval(self.chart_parameters[chart_type][para_name]['regex']))
                    
                    if len(entry.get().split(';')) > 0:
                        entry_list = entry.get().split(';')
                        for e in entry_list:
                            if not regex.search(e):
                                messagebox.showinfo('Input Validation', 'Wrong input format!')
                                return
                        self.tree.set(item, column, entry.get())
                        entry.destroy()
                    else:
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
        entry = Entry(self.tree)  # create edition entry
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
                        
            if column == '#1' or (column == '#2' and len(item.split('_')) == 1):
                x, y, width, height = self.tree.bbox(item, column) 
                value = self.tree.set(item, column)
                # para_name = self.tree.set(item, '#1')
                chart_type = item.split('_')[0]
                if len(item.split('_')) > 1:
                    para_name = item.split('_')[1]
                    options = self.chart_parameters[chart_type][para_name]['options']
                else:
                    options = self.chart_chk_paras[chart_type]['options']
                
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
        val_list = OptionMenu(self.tree, val, options[0], *options)  # create drop-down list
        val_list.place(x=x, y=y, width=width, height=height, anchor='nw')  # display drop-down on top of cell
        val.set(value)  # put former value in entry
        val_list.bind('<FocusOut>', lambda e: val_list.destroy())              
        val.trace('w', ok) # drop-down list value change event 
        val_list.focus_set()
    
    def output_values(self):
        output = {}
        for t in self.tree.get_children():                            
            output[t] = {}            
            for p in self.tree.get_children(t):
                # print(p)
                para_name = p.split('_')[1]
                chart_type = p.split('_')[0]                
                val = str(self.tree.item(p)['values'][0])                
                output[t][para_name] = val
        # print(output)
        return output

    def output_parsed_vals(self, preview):
        output = {}
        for t in self.tree.get_children():
            if not preview and self.tree.item(t)['values'][1] != 'Yes':
                continue                
            output[t] = []
            variant = False
            for p in self.tree.get_children(t):
                # print(p)
                para_name = p.split('_')[1]
                chart_type = p.split('_')[0]
                parser = self.chart_parameters[chart_type][para_name]['parser']
                val = str(self.tree.item(p)['values'][0])
                if len(val.split(';')) > 1:
                    variant = True
                    parsed = self.list_parser(val, parser)
                else:
                    if parser:
                        parsed = eval(parser)
                    else:
                        parsed = val
                output[t].append(parsed)
            if variant:
                var_list = []
                var = []
                self.get_para_var(var, output[t], var_list)
                output[t] = var_list

        # print(output)
        return output, variant

    def list_parser(self, in_str, parser):
        output = []
        in_str_list = in_str.split(';')
        for val in in_str_list:
            if parser:
                parsed = eval(parser)
            else:
                parsed = val
            output.append(parsed)
        return output
    
    def get_para_var(self, para_list_var, para_list, output):    
        # print(para_list_var, para_list)
        # base case: return the variant when the code reach the end of the tree
        if len(para_list) == 0:            
            output.append(para_list_var)
            return output

        # recursive case: keep digging and growing the output
        p = para_list[0]
        # branching when there's a list
        if type(p) == list:            
            for e in p:
                para_list_var_next = para_list_var.copy()
                para_list_var_next.append(e)                            
                para_list_next = para_list.copy()
                para_list_next.pop(0)           
                self.get_para_var(para_list_var_next, para_list_next, output)
        # going to the next element when there isn't
        else:
            para_list_var_next = para_list_var.copy()
            para_list_var_next.append(p) 
            para_list_next = para_list.copy()
            para_list_next.pop(0)
            self.get_para_var(para_list_var_next, para_list_next, output)

    def clear(self):
        self.tree.delete(*self.tree.get_children())
        return
    
    def parameter_chg(self, tree_paras):
        self.clear()
        self.chart_types = tree_paras['chart_types']
        self.chart_parameters = tree_paras['chart_parameters']
        self.chart_chk_paras = tree_paras['chart_chk_paras']
        for i, t in enumerate(self.chart_types):
            self.tree.insert('', tk.END, text=t, value=('', self.chart_chk_paras[t]['value']), tags=self.chart_chk_paras[t]['type'], iid=t, open=False)
            for j, k in enumerate(self.chart_parameters[t].keys()):
                self.tree.insert(t, tk.END, text=k, value=self.chart_parameters[t][k]['value'], tags=self.chart_parameters[t][k]['type'], iid=f'{t}_{k}', open=False)
        return
    
    def set_tree_height(self, height):        
        self.tree.configure(height=height)
        return

    def fold_tree(self):
        for t in self.tree.get_children():
            self.tree.item(t, open=False)
        return
    
    def unfold_tree(self):
        for t in self.tree.get_children():
            self.tree.item(t, open=True)
        return
    
    def deselect_all(self):
        for t in self.tree.get_children():
            self.tree.item(t, values=('', 'No'))
        return

    def select_all(self):
        for t in self.tree.get_children():
            self.tree.item(t, values=('', 'Yes'))
        return


if __name__=='__main__':
    
    chart_json = open('.\\Presets\\chart_default.json', 'r')
    tree_paras = json.load(chart_json)
    chart_json.close()
    # chart_types = chart_paras['chart_types']
    # chart_parameters = chart_paras['chart_parameters']
    # chart_chk_paras = chart_paras['chart_chk_paras']
    
    
    root = tk.Tk()
    para_tree = ChartParaTree(root, tree_paras)
    para_tree.pack(expand=1, fill='both', side='top')
    
    def reload():
        para_tree.parameter_chg(tree_paras)


    test_btn = Button(root, text='Test', command=para_tree.output_values)
    test_btn.pack(side='right')
    clear_btn = Button(root, text='Clear', command=para_tree.clear)
    clear_btn.pack(side='right')
    reload_btn = Button(root, text='Reload', command=reload)
    reload_btn.pack(side='right')

    # fold_btn = Button(root, text='Fold', command=para_tree.fold_tree)
    # fold_btn.pack(side='right')
    # unfold_btn = Button(root, text='Unfold', command=para_tree.unfold_tree)
    # unfold_btn.pack(side='right')

    select_all_btn = Button(root, text='Select All', command=para_tree.select_all)
    select_all_btn.pack(side='right')

    deselect_all_btn = Button(root, text='Deselect All', command=para_tree.deselect_all)
    deselect_all_btn.pack(side='right')
    print(type(para_tree))
    root.mainloop()