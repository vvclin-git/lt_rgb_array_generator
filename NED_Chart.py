
import numpy as np
import cv2
from NED_Types import *

    
def gen_circle_grid(chart_res, grid_dim, marker_size, padding):            
    grid_dim = np.array(grid_dim).astype('uint')
    chart_res = np.array(chart_res).astype('uint')
    padding = np.array(padding).astype('uint')
    grid_x = np.linspace(0 + padding[0], chart_res[0] - padding[0], grid_dim[0]) 
    grid_y = np.linspace(0 + padding[1], chart_res[1] - padding[1], grid_dim[1])
    grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)    
    grid_pitch = (chart_res - 2 * padding) / (grid_dim - 1)
    output_msg = 'Chart Type: Circle Grid\n'
    output_msg += f'Resolution: {chart_res[0]} x {chart_res[1]}\n'
    output_msg += f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, Grid Pitch: {grid_pitch[0]} x {grid_pitch[1]}\n'
    output_msg += f'Dot Size: {marker_size}\n'
    output_msg += f'Padding: {padding[0]}x{padding[1]}\n'
    print(f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, ', end='')
    print(f'Grid Pitch: {grid_pitch[0]} x {grid_pitch[1]}')
    print(f'Dot Size: {marker_size}')
    print(f'Padding: {padding[0]}x{padding[1]}')
    chart_im = np.zeros((chart_res[1], chart_res[0], 3))
    grid_coords = np.vstack((grid_xx.flatten(), grid_yy.flatten())).transpose().astype('int')
    
    for i in range(len(grid_coords)):
        cv2.circle(chart_im, (grid_coords[i, 0], grid_coords[i, 1]), marker_size, (255, 255, 255), -1)
    
    return chart_im, output_msg, Grid(grid_coords, grid_dim)

def gen_grille(chart_res, width, orient):
    if orient == 'vertical':
        grid_dim = np.array([chart_res[0] / (width * 2) + 1, 2]).astype('uint')
        grille_size = np.array([width, chart_res[1]])
    elif orient == 'horizontal':
        grid_dim = np.array([2, chart_res[1] / (width * 2) + 1]).astype('uint')
        grille_size = np.array([chart_res[0], width])
    else:
        raise Exception('Invalid orientation (horizontal / vertical)')            
        
    grid_x = np.linspace(0, chart_res[0], grid_dim[0]) 
    grid_y = np.linspace(0, chart_res[1], grid_dim[1])
    grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)    
    grid_pitch = (chart_res) / (grid_dim - 1)
    output_msg = 'Chart Type: Grille\n'
    output_msg += f'Resolution: {chart_res[0]} x {chart_res[1]}\n'
    output_msg += f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, Grid Pitch: {grid_pitch[0]} x {grid_pitch[1]}\n'
    output_msg += f'Grille Size: {grille_size[0]} x {grille_size[1]}\n'
    
    print(f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, ', end='')
    print(f'Grid Pitch: {grid_pitch[0]} x {grid_pitch[1]}')
    print(f'Grille Size: {grille_size[0]} x {grille_size[1]}')
    chart_im = np.zeros((chart_res[1], chart_res[0], 1)).astype('uint8')
    grid_coords = np.vstack((grid_xx.flatten(), grid_yy.flatten())).transpose().astype('int')

    for p in grid_coords:
        pt_1 = np.array([p[0], p[1]])
        pt_2 = pt_1 + grille_size - 1
        cv2.rectangle(chart_im, [*pt_1], [*pt_2], (255), -1)
        
    return chart_im, output_msg, grid_coords

def gen_checkerboard(chart_res, grid_dim, begin_with, padding):
    chart_res = np.array(chart_res).astype('uint')
    padding = np.array(padding).astype('uint')
    grid_dim = np.array(grid_dim).astype('uint')        
    grid_x = np.linspace(0 + padding[0], chart_res[0] - padding[0], grid_dim[0], endpoint=False) 
    grid_y = np.linspace(0 + padding[1], chart_res[1] - padding[1], grid_dim[1], endpoint=False)
    grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)    
    grid_pitch = ((chart_res - 2 * padding) / (grid_dim)).astype('uint')
    output_msg = 'Chart Type: Checkerboard\n'
    output_msg += f'Resolution: {chart_res[0]} x {chart_res[1]}\n'
    output_msg += f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, Square Size: {grid_pitch[0]} x {grid_pitch[1]}\n'
    output_msg += f'Padding: {padding[0]}x{padding[1]}\n'
    
    print(f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, ', end='')
    print(f'Square Size: {grid_pitch[0]} x {grid_pitch[1]}')    
    print(f'Padding: {padding[0]}x{padding[1]}')
    chart_im = np.zeros((chart_res[1], chart_res[0], 3))
    grid_coords = np.vstack((grid_xx.flatten(), grid_yy.flatten())).transpose().astype('int')
    
    fill_val_start = {'black':0, 'white':1}
    fill_val = fill_val_start[begin_with]    

    for i, p in enumerate(grid_coords):
        pt_1 = np.array([p[0], p[1]])
        pt_2 = pt_1 + grid_pitch                
        cv2.rectangle(chart_im, [*pt_1], [*pt_2], ([fill_val * 255] * 3), -1)        
        prev_fill = fill_val
        # for even column number
        if grid_dim[0] % 2 == 0:
            # the filled color should repeat itself in the beginning of the next row
            if ((i + 1) % grid_dim[0]) == 0:
                if prev_fill == 1:
                    prev_fill = 0
                else:
                    prev_fill = 1
        if prev_fill == 0:
            fill_val = 1
        else:
            fill_val = 0    
    
    grid_coords = (grid_coords + grid_pitch * 0.5).astype('uint')

    return chart_im, output_msg, grid_coords

def draw_se_MTF_pattern(chart_im, center, edge_angle, pattern_size, line_type):    
    anchor = center - 0.5 * pattern_size
    pt1 = anchor + np.array([0, pattern_size])
    pt2 = pt1 + np.array([0.5 * pattern_size * (1 - np.tan(np.radians(edge_angle))), 0])
    pt3 = pt2 + np.array([0.5 * pattern_size * (np.tan(np.radians(edge_angle))), -pattern_size])    
    pts = np.array([anchor, pt1, pt2, pt3, anchor]).astype('int32')
    pts = np.expand_dims(pts, axis=1)  
    cv2.fillPoly(chart_im, [pts], color=(255, 255, 255), lineType=line_type)
    return chart_im, None

def gen_se_MTF(chart_res, grid_dim, edge_angle, pattern_size, padding, line_type):
    grid_dim = np.array(grid_dim).astype('uint')        
    chart_res = np.array(chart_res).astype('uint')
    padding = np.array(padding).astype('uint')
    grid_x = np.linspace(0 + padding[0], chart_res[0] - padding[0], grid_dim[0], endpoint=False) 
    grid_y = np.linspace(0 + padding[1], chart_res[1] - padding[1], grid_dim[1], endpoint=False)
    grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)    
    grid_pitch = ((chart_res - 2 * padding) / (grid_dim)).astype('uint')
    output_msg = 'Chart Type: Slanted Edge MTF\n'
    output_msg += f'Resolution: {chart_res[0]} x {chart_res[1]}\n'
    output_msg += f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, Square Size: {grid_pitch[0]} x {grid_pitch[1]}\n'
    output_msg += f'Padding: {padding[0]}x{padding[1]}\n'
    
    print(f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, ', end='')
    print(f'Square Size: {grid_pitch[0]} x {grid_pitch[1]}')    
    print(f'Padding: {padding[0]}x{padding[1]}')
    chart_im = np.zeros((chart_res[1], chart_res[0], 3), dtype='uint8')
    grid_coords = np.vstack((grid_xx.flatten(), grid_yy.flatten())).transpose().astype('int')
    grid_coords = (grid_coords + np.array([pattern_size * 0.5, pattern_size * 0.5])).astype('uint')
    
    for p in grid_coords:
        chart_im, _ = draw_se_MTF_pattern(chart_im, p, edge_angle, pattern_size, line_type)    

    return chart_im, output_msg, grid_coords



def gen_reticle(chart_res, color, cross_size, marker_size, thickness):
    chart_im = np.zeros((chart_res[1], chart_res[0], 3))
    # Center
    cv2.drawMarker(chart_im, np.array([chart_res[0] * 0.5, chart_res[1] * 0.5], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=cross_size, thickness=thickness)
    # Left Top
    center = (np.array([0, 0]) + np.array([marker_size * 0.5, marker_size * 0.5])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([0, 0], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Left Center
    center = (np.array([0, chart_res[1] * 0.5]) + np.array([marker_size * 0.5, 0])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([0, chart_res[1] * 0.5], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Left Bottom
    center = (np.array([0, chart_res[1]]) + np.array([marker_size * 0.5, marker_size * -0.5])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([0, chart_res[1]], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Center Top
    center = (np.array([chart_res[0] * 0.5, 0]) + np.array([0, marker_size * 0.5])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([chart_res[0] * 0.5, 0], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Center Bottom
    center = (np.array([chart_res[0] * 0.5, chart_res[1]]) + np.array([0, marker_size * -0.5])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([chart_res[0] * 0.5, chart_res[1]], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Right Top
    center = (np.array([chart_res[0], 0]) + np.array([marker_size * -0.5, marker_size * 0.5])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([chart_res[0], 0], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Right Center
    center = (np.array([chart_res[0], chart_res[1] * 0.5]) + np.array([marker_size * -0.5, 0])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([chart_res[0], chart_res[1] * 0.5], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Right Botoom
    center = (np.array([chart_res[0], chart_res[1]]) + np.array([marker_size * -0.5, marker_size * -0.5])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([chart_res[0], chart_res[1]], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    output_msg = 'Chart Type: Reticle\n'
    output_msg += f'Resolution: {chart_res[0]} x {chart_res[1]}\n'
    output_msg += f'Cross size: {cross_size}, Marker Size: {marker_size}\n'
    
    
    return chart_im, output_msg, None



if __name__ == '__main__':

    chart_res = np.array([2560, 1440])
    chart_im = gen_reticle(chart_res, (0, 255, 0), 8)
    cv2.imwrite('reticle_test.bmp', chart_im)
    grid_dim = np.array([16, 9])
    padding = np.array([0, 0])

    chart_coords, chart_im = gen_se_MTF(chart_res, grid_dim, 11.25, 100, padding, cv2.LINE_8)

    cv2.imwrite('se_MTF_test_20220104.png', chart_im)

    for p in chart_coords:
        p1 = p - np.array([50, 50])
        p2 = p + np.array([50, 50])
        cv2.rectangle(chart_im, p1, p2, color=(0, 255, 0), thickness=5)

    cv2.imwrite('se_MTF_annotated_20220104.png', chart_im)


