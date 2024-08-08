import numpy as np
import cv2

def calculate_dim(px_size, px_pitch, px_num):
    # Calculate dimension
    return (px_size[0] + px_pitch[0] * (px_num[0] - 1), 
            px_size[1] + px_pitch[1] * (px_num[1] - 1))

def gen_pixel(canvas, px_scale, px_pos, px_size, sub_px_size, sub_px_pitch, sub_px_order):
    sub_px_padx = px_size[0]
    top_left_x, top_left_y = px_pos + sub_px_pad    
    bottom_right_x = top_left_x + 
    bottom_right_y = top_left_y + sub_px_size_p[1]
    cv2.rectangle(canvas, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), 255, -1)
    cv2.rectangle(canvas_preview, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), 255, -1)
    return

def gen_array(px_scale, px_num, px_pitch, px_size, row_offset, sub_px_size, sub_px_pitch, sub_px_order):
    dim = calculate_dim(px_size, px_pitch, px_num)
    output_res = (int(dim[1] * px_scale), int(dim[0] * px_scale))
    canvas = np.zeros(output_res, dtype=np.uint8)
    canvas_preview = np.zeros_like(canvas)
    # Calculate pattern size, pitch, and shift in pixel units
    # px_size_p = (int(px_size[0] * px_scale), int(px_size[1] * px_scale))
    px_pitch_p = (int(px_pitch[0] * px_scale), int(px_pitch[1] * px_scale))
    sub_px_size_p = (int(sub_px_size[0] * px_scale), int(sub_px_size[1] * px_scale))
    sub_px_pitch_p = (int(sub_px_pitch[0] * px_scale), int(sub_px_pitch[1] * px_scale))

    # Create patterns with shift
    for j in range(res[1]):
        for i in range(res[0]):
            top_left_x = i * (px_pitch_p[0]) + shift_multiplier * sub_px_pitch_p[0]
            top_left_y = j * (px_pitch_p[1])
            bottom_right_x = top_left_x + sub_px_size_p[0]
            bottom_right_y = top_left_y + sub_px_size_p[1]
            cv2.rectangle(canvas, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), 255, -1)
            cv2.rectangle(canvas_preview, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), 255, -1)
            pattern_preview[:, :, rgb_bgr[color]] = canvas_preview
            # print(f'{top_left_x}, {top_left_y}')