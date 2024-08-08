# -*- coding: utf-8 -*-
# Advanced zoom example. Like in Google Maps.
# It zooms only a tile, but not the whole image. So the zoomed tile occupies
# constant memory and not crams it with a huge resized image for the large zooms.

import random
import tkinter as tk
from tkinter.ttk import *
from PIL import Image, ImageTk
from matplotlib import container
import cv2
import numpy as np
from dataclasses import dataclass

@dataclass
class Overlay:
    im: np.ndarray
    chk: int
    btn: Button

class AutoScrollbar(Scrollbar):
    ''' A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager '''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')


class Zoom_Advanced(Frame):
    ''' Advanced zoom of the image '''
    def __init__(self, mainframe, image):
        ''' Initialize the main Frame '''
        Frame.__init__(self, master=mainframe)
        # self.master.title('Zoom with mouse wheel')
        # Vertical and horizontal scrollbars for canvas
        self.vbar = AutoScrollbar(self.master, orient='vertical')
        self.hbar = AutoScrollbar(self.master, orient='horizontal')
        self.vbar.grid(row=0, column=1, sticky='ns')
        self.hbar.grid(row=1, column=0, sticky='we')
        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.master, highlightthickness=0,
                                xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.update()  # wait till canvas is created
        self.vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
        self.hbar.configure(command=self.scroll_x)
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<ButtonPress-1>', self.move_from)
        self.canvas.bind('<B1-Motion>',     self.move_to)
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',   self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>',   self.wheel)  # only with Linux, wheel scroll up
        # self.image = Image.open(path)  # open image
        self.image = image  # open image
        self.im = np.asarray(self.image)[:, :, ::-1]
        self.overlays = {}
        # self.overlays_chk_vals = []
        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0, tags='container')
        self.imageid = None
        self.last_overlay_only = False
        # Plot some optional random rectangles for the test purposes
        # minsize, maxsize, number = 5, 20, 10
        # for n in range(number):
        #     x0 = random.randint(0, self.width - maxsize)
        #     y0 = random.randint(0, self.height - maxsize)
        #     x1 = x0 + random.randint(minsize, maxsize)
        #     y1 = y0 + random.randint(minsize, maxsize)
        #     color = ('red', 'orange', 'yellow', 'green', 'blue')[random.randint(0, 4)]
        #     self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, activefill='black')
        
        # overlay control widgets
        self.overlay_ctrl_frame = Frame(self.canvas)
        self.overlay_ctrl_frame.bind('<Expose>', self.on_expose)
        self.overlay_ctrl_window = self.canvas.create_window(10, 10, anchor=tk.NW, window=self.overlay_ctrl_frame)        
        self.show_image()

    def scroll_y(self, *args, **kwargs):
        ''' Scroll canvas vertically and redraw the image '''
        self.canvas.yview(*args, **kwargs)  # scroll vertically
        self.show_image()  # redraw the image

    def scroll_x(self, *args, **kwargs):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview(*args, **kwargs)  # scroll horizontally
        self.show_image()  # redraw the image

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)
        # canvas_x, canvas_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        # print(f'move starting from {event.x}, {event.y}, {canvas_x}, {canvas_y}')

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        # print(f'move finished at {event.x}, {event.y}')
        self.show_image()  # redraw the image

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        else: return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale        /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale        *= self.delta
        self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        # print(x, y, scale)
        self.show_image()


    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        bbox1 = self.canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.canvas.configure(scrollregion=bbox)  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not            
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            if self.imageid == None:
                self.imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                               anchor='nw', image=imagetk, tags='view_img')
            else:
                self.canvas.delete('view_img')
                self.imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                               anchor='nw', image=imagetk, tags='view_img')               
            self.canvas.lower(self.imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection
        # print(len(self.canvas.find_withtag('view_img')), len(self.canvas.find_all()))
        # print(f'container dim: {self.get_contianer_dim()}, container center: {self.get_container_center()}, imscale: {self.imscale} view: {self.canvas.xview()}, {self.canvas.yview()}')
        # print(f'horizontal scroll location: {self.hbar.get()}, vertical scroll location: {self.vbar.get()}')
        
    def center_view(self):        
        # print(f'horizontal scroll location: {self.hbar.get()}, vertical scroll location: {self.vbar.get()}')
        hbar_loc = self.hbar.get()
        vbar_loc = self.vbar.get()
        hbar_len = hbar_loc[1] - hbar_loc[0]
        vbar_len = vbar_loc[1] - vbar_loc[0]
        self.canvas.xview_moveto((1-hbar_len) * 0.5)
        self.canvas.yview_moveto((1-vbar_len) * 0.5)
        self.show_image()
        pass

    def scale_to_canvas(self):
        self.center_view()        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        container_width, container_height = self.get_contianer_dim()
        scale = canvas_width / container_width
        if container_height * scale > canvas_height:
            scale = canvas_height / container_height
        
        x, y = int(container_width * 0.5), int(container_height * 0.5)
                
        self.imscale = scale  
        self.canvas.scale('all', x, y, scale, scale)      
        self.show_image()  
        return    

    def update_image(self, img):
        self.image = img
        self.im = np.asarray(img)        
        self.width, self.height = self.image.size
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0, tags='container')
        self.clean_overlay()
        self.show_image()
        self.update()
        self.scale_to_canvas()
        return
        # print(f'after loading horizontal scroll location: {self.hbar.get()}, vertical scroll location: {self.vbar.get()}')
    
    def update_im(self, im):
        im = im[:, :, ::-1].astype('uint8')
        if im.shape[2] != 3:
            im = np.dstack((im, im, im))
        self.image = Image.fromarray(im)
        self.im = im
        self.width, self.height = self.image.size
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0, tags='container')
        self.clean_overlay()
        self.show_image()
        self.update()
        self.scale_to_canvas()
        return
    
    def get_contianer_dim(self):
        bbox1 = self.canvas.bbox(self.container)
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        container_width = bbox1[2] - bbox1[0]
        container_height = bbox1[3] - bbox1[1]
        return container_width, container_height

    def get_container_center(self):
        bbox1 = self.canvas.bbox(self.container)
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        container_width, container_height = self.get_contianer_dim()
        container_x, container_y = int(bbox1[0] + container_width * 0.5), int(bbox1[1] + container_height * 0.5)
        return container_x, container_y

    def apply_overlay(self, im, overlay):
        if im.shape != overlay.shape:
            raise TypeError('inconsistent image types!')
        else:            
            overlay_bw = cv2.cvtColor(overlay, cv2.COLOR_BGR2GRAY)
            _, overlay_mask = cv2.threshold(overlay_bw, 5, 255, cv2.THRESH_BINARY)
            overlay_mask_inv = cv2.bitwise_not(overlay_mask)
            im_subs = cv2.bitwise_and(im, im, mask=overlay_mask_inv)
            overlay_front = cv2.bitwise_and(overlay, overlay, mask=overlay_mask)
            output = cv2.add(im_subs, overlay_front)
        return output
    
    def add_overlay(self, overlay_im, overlay_name):        
        if overlay_im.shape != self.im.shape:
            raise TypeError('inconsistent image types!')
        if self.last_overlay_only:
            self.hide_overlay()
        if overlay_name not in self.overlays.keys():
            chk_val = tk.IntVar()            
            chk_btn = Checkbutton(self.overlay_ctrl_frame, text=overlay_name, variable=chk_val, command=self.output_overlay)
            chk_btn.pack(side='top', expand=1, fill='both')                
            self.overlays[overlay_name] = Overlay(im=overlay_im, chk=chk_val, btn=chk_btn)
        else:
            self.overlays[overlay_name].im = overlay_im
        self.overlays[overlay_name].chk.set(1)
        self.output_overlay()        
        return

    def output_overlay(self):
        if len(self.overlays) > 0:
            output = self.im.copy()
            for o in self.overlays.values():
                if o.chk.get() == 1:
                    output = self.apply_overlay(output, o.im)
            self.image = Image.fromarray(output[:, :, ::-1])
            self.show_image()
        return

    def hide_overlay(self):
        for o in self.overlays.values():
            o.chk.set(0)
        self.output_overlay()
        return

    def clean_overlay(self):
        self.image = Image.fromarray(self.im[:, :, ::-1])        
        for o in self.overlays.values():
            o.btn.destroy()
        self.overlays = {}
        self.show_image()
        return
    
    # event handler for children-less widget shrinking
    def on_expose(self, event):
        w = event.widget
        if not w.children:
            w.configure(height=1)


if __name__ == '__main__':

    img = Image.open('.\\Temp\\test_img.png').convert('RGB')  # place path to your image here
    im = cv2.imread('.\\Temp\\test_img.png')
    root = tk.Tk()
    canvas_frame = tk.Frame(root)    
    canvas_frame.pack(side='top')
    app = Zoom_Advanced(canvas_frame, img)
    
    overlay_1 = np.zeros_like(im)
    overlay_2 = np.zeros_like(im)

    cv2.circle(overlay_1, (400, 400), 200, (0, 255, 0), -1)
    cv2.rectangle(overlay_2, (100, 100), (500, 500), (0, 0, 255), -1)
    
    # app.add_overlay(overlay_1, 'overlay_1')
    # app.add_overlay(overlay_2, 'overlay_2')
    

    def add_overlay_1():
        overlay_1 = np.zeros_like(im)
        cv2.circle(overlay_1, (400, 400), 200, (0, 255, 0), -1)
        app.add_overlay(overlay_1, 'overlay_1')
        return
    
    def add_overlay_2():
        overlay_2 = np.zeros_like(im)
        cv2.rectangle(overlay_2, (100, 100), (500, 500), (0, 0, 255), -1)
        app.add_overlay(overlay_2, '2')
        return

    def update_overlay_2():
        overlay_2 = np.zeros_like(im)
        cv2.rectangle(overlay_2, (100, 100), (500, 500), (0, 0, 255), 1)
        app.add_overlay(overlay_2, 'overlay_2')
        return

    def toggle_show_last():
        if app.last_overlay_only:
            app.last_overlay_only = False
        else:
            app.last_overlay_only = True
        return

    print(app.canvas.winfo_height(), app.canvas.winfo_width())
    app.canvas.configure(width=640, height=480)
    app.show_image()
    test_btn = tk.Button(root, text='test', command=app.scale_to_canvas)
    test_btn.pack(side='top')
    test_btn_2 = tk.Button(root, text='test_2', command=app.center_view)
    test_btn_2.pack(side='top')
    test_btn_3 = tk.Button(root, text='add overlay 1', command=add_overlay_1)
    test_btn_3.pack(side='top')
    test_btn_4 = tk.Button(root, text='add overlay 2', command=add_overlay_2)
    test_btn_4.pack(side='top')
    test_btn_5 = tk.Button(root, text='update overlay 2', command=update_overlay_2)
    test_btn_5.pack(side='top')
    test_btn_6 = tk.Button(root, text='hide overlay', command=app.hide_overlay)
    test_btn_6.pack(side='top')
    test_btn_7 = tk.Button(root, text='clean overlay', command=app.clean_overlay)
    test_btn_7.pack(side='top')
    test_btn_8 = tk.Button(root, text='show last only', command=toggle_show_last)
    test_btn_8.pack(side='top')
    
    chk_box_frame = Frame(app)
    chk_box_frame.pack(side='top')

    chk_box_1 = Checkbutton(app, text='overlay_1')
    chk_box_1.pack(side='top')

    root.mainloop()



