import numpy as np
import cv2
import textwrap
import time

def calculate_dim(px_size, px_pitch, px_num):
    # Calculate dimension
    return (px_size[0] + px_pitch[0] * (px_num[0] - 1), 
            px_size[1] + px_pitch[1] * (px_num[1] - 1))

def gen_LT_grid_fn(px_scale, px_num, px_pitch, px_size):    
    px_pitch = (np.array(px_pitch) * px_scale).astype('uint')
    px_num =  (np.array(px_num)).astype('uint')
    output_res = (px_pitch * px_num)
    dim = output_res / px_scale
    header = f"MESH: {output_res[1]} {output_res[0]} {dim[0] / 1000 * (-0.5)} {dim[1] / 1000 * (-0.5)} {dim[0] / 1000 * 0.5} {dim[1] / 1000 * 0.5}"    
    output_fn = f'px scale {px_scale}_{px_size[0]}x{px_size[1]}_{px_num[0]}x{px_num[1]}_{dim[0]}x{dim[1]}'        
    return header, output_fn

def parse_sub_pixel(sub_px_order):
    sub_px_list = sub_px_order.split('|')
    output = []
    # if len(sub_px_list) == 1:
    #     output.append(list(sub_px_order))
    #     return 
    for r in sub_px_list:
        output.append(list(r))
    return output

def gen_pixel(canvas, px_pos, sub_px_pad, sub_px_size, sub_px_pitch, sub_px_order_str):    
    sub_px_order = parse_sub_pixel(sub_px_order_str)
    sub_px_size_dict = {'R':None, 'G':None, 'B':None, 'W':None}
    sub_px_color = {'R':(0, 0, 255), 'G':(0, 255, 0), 'B':(255, 0, 0), 'W':(255, 255, 255)}
    if not isinstance(sub_px_size, list):       
        sub_px_size_dict = {k:sub_px_size for k in sub_px_size_dict.keys()}
    else:
        sub_px_size_dict['R'] = sub_px_size[0]
        sub_px_size_dict['G'] = sub_px_size[1]
        sub_px_size_dict['B'] = sub_px_size[2]
        sub_px_size_dict['W'] = sub_px_size[3]

    for j, r in enumerate(sub_px_order):
        for i, c in enumerate(r):
            top_left_x, top_left_y = (px_pos[0] + sub_px_pad[0] + i * sub_px_pitch[0]), (px_pos[1] + sub_px_pad[1] + j * sub_px_pitch[1])
            bottom_right_x, bottom_right_y = (top_left_x + sub_px_size_dict[c][0]), (top_left_y + sub_px_size_dict[c][1])
            cv2.rectangle(canvas, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), sub_px_color[c], -1)      
    return canvas

def draw_pixel_frame(canvas, px_scale, px_pitch, px_size):
    px_pitch = (np.array(px_pitch) * px_scale).astype('uint')
    px_size = (np.array(px_size) * px_scale).astype('uint')
    px_orig_pos = np.array([0, 0], dtype='uint') + 0.5 * (px_pitch - px_size)
    px_orig_pos = px_orig_pos.astype('uint')
    top_left_x, top_left_y = px_orig_pos
    bottom_right_x, bottom_right_y = px_orig_pos + px_size
    cv2.rectangle(canvas, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 255, 255), 1)
    return canvas

def gen_array(px_scale, px_num, px_pitch, px_size, row_offset, sub_px_pitch, sub_px_size, sub_px_pad, sub_px_order):
    px_pitch = (np.array(px_pitch) * px_scale).astype('uint')
    px_size = (np.array(px_size) * px_scale).astype('uint')
    px_num = np.array(px_num)
    # array_size = px_pitch * (px_num - 1) + px_size
    array_size = px_pitch * px_num
    array_im = np.zeros([array_size[1], array_size[0], 3], dtype='uint8')
    sub_px_pitch = (np.array(sub_px_pitch) * px_scale).astype('uint')
    # sub_px_size = ((np.array(s).astype('uint8') * px_scale) for s in sub_px_size)
    if isinstance(sub_px_size, list):
        sub_px_size = [(np.array(s).astype('uint') * px_scale) for s in sub_px_size]
    else:
        sub_px_size = (int(sub_px_size[0] * px_scale), int(sub_px_size[1] * px_scale))
    sub_px_pad = (np.array(sub_px_pad) * px_scale).astype('uint')
    # px_pos = np.array([0, 0])
    # px_orig_pos = np.array([0, 0], dtype='uint8')
    px_orig_pos = np.array([0, 0], dtype='uint') + 0.5 * (px_pitch - px_size)
    px_orig_pos = px_orig_pos.astype('uint')
    for j in range(px_num[1]):
        # px_pos = np.array([0, 0]) + np.array([px_pos[0] + row_offset * (j % 2) * px_pitch[0], 0])
        px_orig_pos = px_orig_pos + np.array([row_offset * (j % 2) * px_pitch[0], 0], dtype='uint8')
        for i in range(px_num[0]):
            px_pos = px_orig_pos + px_pitch * (np.array([i, j]))
            if isinstance(sub_px_order, list):
                gen_pixel(array_im, px_pos, sub_px_pad, sub_px_size, sub_px_pitch, sub_px_order[j % len(sub_px_order)])
            else:
                gen_pixel(array_im, px_pos, sub_px_pad, sub_px_size, sub_px_pitch, sub_px_order)
    
    output_msg = (
        f'Array Size: {(array_size / px_scale)[0]} x {(array_size / px_scale)[1]}\n'
        f'Array Dimension: {px_num[0]} x {px_num[1]}\n'
        f'Pixel Pitch: {px_pitch[0] / px_scale} x {px_pitch[1] / px_scale}\n'
        f'Pattern File Resolution: {array_size[0]} x {array_size[1]} (1 Pixel = {1 / px_scale} µm)\n'
    )
    
    return array_im, output_msg