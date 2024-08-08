
import numpy as np

class Coords:
    def __init__(self, coords):
        self.coords = coords
        self.orig_coords = coords                
        return      

    def normalize(self):
        centroid = self.get_centroid()
        # centroid_x = np.average(self.coords[:, 0])
        # centroid_y = np.average(self.coords[:, 1])
        centroid_dist = self.get_pt_dist(centroid)
        # centroid_dist = np.sqrt(np.power((self.coords[:, 0] - centroid_x), 2) + np.power((self.coords[:, 1] - centroid_y), 2))
        nearest_pts = self.coords[centroid_dist.argsort(), :][0:4, :]
        y_dist = abs(nearest_pts[:, 1] - nearest_pts[0, 1])
        x_dist = abs(nearest_pts[:, 0] - nearest_pts[0, 0])
        x_dist.sort()
        y_dist.sort()
        min_x_pitch = np.average(x_dist[2:])
        min_y_pitch = np.average(y_dist[2:])        
        coords_norm = np.zeros_like(self.coords)
        coords_norm[:, 0] = self.coords[:, 0] / min_x_pitch
        coords_norm[:, 1] = self.coords[:, 1] / min_y_pitch
        self.coords = coords_norm
        return
    
    def get_dim(self):
        coords_width = self.coords[:, 0].max() - self.coords[:, 0].min()
        coords_height = self.coords[:, 1].max() - self.coords[:, 1].min()
        return np.array([coords_width, coords_height])

    def get_pt_dist(self, pt):
        pt_vect = np.tile(pt, (len(self.coords), 1))
        center_dist = np.sqrt(np.power((self.coords[:, 0] - pt_vect[:, 0]), 2) + np.power((self.coords[:, 1] - pt_vect[:, 1]), 2))
        return center_dist

    def get_centroid(self):
        return np.array([np.average(self.coords[:, 0]), np.average(self.coords[:, 1])])  

    def shift_coords(self, shift):
        self.coords = self.coords + shift
        return

    def get_neighbors(self, pt, coords, max_ratio):        
        coords_dist = self.get_pt_dist(pt)        
        close_neighbhors = coords_dist[coords_dist < coords_dist.min() * max_ratio]
        ind = close_neighbhors.argsort()        
        # neighbors = coords[ind]
        neighbors = close_neighbhors[ind]
        return neighbors

    def scale_coords(self, scale):
        self.coords = self.coords * scale
        return
    
    def restore_coords(self):
        self.coords = self.orig_coords
        return

class Grid(Coords):
    def __init__(self, coords, grid_dim):
        if (grid_dim[0] * grid_dim[1]) != len(coords):
            raise Exception(f"Invalid grid dimension! (grid_dim={grid_dim}, coords length={len(coords)})")    
        super().__init__(coords)
        self.grid_dim = grid_dim
        self.sorted = False
        self.center_ind = None           
    
    def get_next_pt(self, pt, dist_angle, max_ratio):    
        # pt_vect = np.tile(pt, (len(self.coords), 1))
        # coords_dist = np.sqrt(np.power((self.coords[:, 0] - pt_vect[:, 0]), 2) + np.power((self.coords[:, 1] - pt_vect[:, 1]), 2))
        coords_dist = self.get_pt_dist(pt)
        # neighbors = self.coords[np.argwhere((coords_dist > 0) & (coords_dist < coords_dist[coords_dist.nonzero()].min() * max_ratio))]
        neighbors = self.coords[np.argsort(coords_dist)][1:5]
        neighbors = neighbors.squeeze()
        pt_vect = np.tile(pt, (len(neighbors), 1))
        neighbors_theta = abs(np.arctan2((neighbors - pt_vect)[:, 1], (neighbors - pt_vect)[:, 0]))    
        next_pt = np.atleast_2d(neighbors[neighbors_theta.argsort()])[0]
        
        if neighbors_theta.min() > np.deg2rad(dist_angle):
            return None
        
        return next_pt

    def sort(self, dist_angle, max_ratio):
        left_col = self.coords[self.coords[:, 0].argsort()[0:self.grid_dim[1]]]
        left_col = left_col[(left_col[:, 1]).argsort()]
        self.sorted_coords = np.zeros_like(self.coords)
        ind = 0
        for p in left_col:        
            next_pt = p
            for i in range(self.grid_dim[0]):
                self.sorted_coords[ind] = next_pt                    
                next_pt = self.get_next_pt(next_pt, dist_angle, max_ratio)
                # if next_pt is None:
                #     print(f'Unable to find the next point of point {ind} at {p}') 
                ind += 1    
        self.coords = self.sorted_coords
        self.orig_coords = self.sorted_coords
        self.sorted = True
        
        if self.grid_dim[0] % 2 == 0:
            center_ind_x = np.array([self.grid_dim[0] / 2 - 1, self.grid_dim[0] / 2]).astype('uint')
        else:
            center_ind_x = np.array([int(self.grid_dim[0] / 2)])
        if self.grid_dim[1] % 2 == 0:
            center_ind_y = np.array([self.grid_dim[1] / 2 - 1, self.grid_dim[1] / 2]).astype('uint')
        else:
            center_ind_y = np.array([int(self.grid_dim[1] / 2)])
        center_ind_xx, center_ind_yy = np.meshgrid(center_ind_x, center_ind_y)
        
        self.center_ind = (center_ind_yy * self.grid_dim[0] + center_ind_xx).flatten()
        self.left_ind = (center_ind_yy * self.grid_dim[0]).flatten()
        self.right_ind = (center_ind_yy * self.grid_dim[0] + (self.grid_dim[0] - 1)).flatten()
        self.top_ind = center_ind_xx.flatten()
        self.bottom_ind = ((self.grid_dim[1] - 1) * self.grid_dim[0] + center_ind_xx).flatten()
        
        return

    def get_center_dim(self):
        center_width = abs(np.average(self.coords[self.right_ind, 0]) - np.average(self.coords[self.left_ind, 0]))
        center_height = abs(np.average(self.coords[self.top_ind, 1]) - np.average(self.coords[self.bottom_ind, 1]))
        return np.array([center_width, center_height])

    def center_grid(self, std_grid):
        if not self.sorted:
            print('Coordinate not indexed!')
            return
        if np.any(std_grid.grid_dim != self.grid_dim):
            raise Exception("Invalid grid dimension!") 

        std_grid_center = np.array([np.average(std_grid.coords[self.center_ind, 0]), np.average(std_grid.coords[self.center_ind, 1])])     
        grid_center = np.array([np.average(self.coords[self.center_ind, 0]), np.average(self.coords[self.center_ind, 1])])        
        
        coords_shift = std_grid_center - grid_center
        self.shift_coords(coords_shift)            
        return

    def copy(self):
        return Grid(self.coords, self.grid_dim)
    
    def get_center_pt(self):        
        if not self.sorted:
            return None
        center_pt = np.atleast_2d(self.coords[self.center_ind].squeeze())
        if center_pt.shape[0] > 1:
            center_pt = np.average(center_pt, axis=0)
        return center_pt

class ROI():
    def __init__(self, roi_coord, roi_shape, camera_eff, sensor_size, pixel_size, weight):               
        
        self.roi_coord = np.array(roi_coord)
        self.shape = np.array(roi_shape)
        self.sensor_size = np.array(sensor_size)
        self.pt1 = self.roi_coord - (self.shape * 0.5).astype('int')
        self.pt2 = self.roi_coord + (self.shape * 0.5).astype('int')        
        self.weight = weight
        
        pixel_size = np.array(pixel_size)
        
        sensor_center_coord_real = (self.sensor_size * 0.5)
        self.roi_coord_real = self.roi_coord * pixel_size - sensor_center_coord_real
        self.roi_dist_real = np.linalg.norm(self.roi_coord_real)
        self.alpha = np.arctan(self.roi_dist_real / camera_eff)
        if self.roi_coord_real[0] > 0 and self.roi_coord_real[1] > 0:
            self.phi = np.arctan(self.roi_coord_real[0] / self.roi_coord_real[1])
        elif self.roi_coord_real[0] > 0 and self.roi_coord_real[1] == 0:
            self.phi = np.pi * 0.5
        elif self.roi_coord_real[0] > 0 and self.roi_coord_real[1] < 0:
            self.phi = np.pi + np.arctan(self.roi_coord_real[0] / self.roi_coord_real[1])
        elif self.roi_coord_real[0] <= 0 and self.roi_coord_real[1] < 0:
            self.phi = np.pi + np.arctan(self.roi_coord_real[0] / self.roi_coord_real[1])
        elif self.roi_coord_real[0] < 0 and self.roi_coord_real[1] == 0:
            self.phi = np.pi * 1.5
        elif self.roi_coord_real[0] <= 0 and self.roi_coord_real[1] > 0:
            self.phi = 2 * np.pi + np.arctan(self.roi_coord_real[0] / self.roi_coord_real[1])

