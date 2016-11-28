# -*- coding: utf-8 -*-

"""
/***************************************************************************
 LambertGrid
                                 lambert grid defination
 general grid defination and related operations
                              -------------------
        begin                : 2016-11-14
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
partition equal-area grids using Lambert cylindrical equal-area projection
The Formulae is:
x = longitude - central_meridian
y = sin(latitude)

 We split raster/vector data into small grids. 
 To efficiently organize these small grids, we merge small grids into big grids. 
 We use google's protobuf format to define big grids, which is called GridData, you can refere protoc/grid_data.protoc for detail.

 This class defines the spatial info and spatial operations(including giving an extent, calculating how many big grids and small grids within it)

The most important spatial info about Grid is grid resolution and grid width/height,
grid resolution means how many meters a small grid represents, and grid width/height defines how many small grid(along width and height) a big grid contains.

grid area(km2) of each level
(0, 255603946.7)                                                            
(1, 63900986.7)                                                            
(2, 15975246.7)                                                            
(3, 3993811.7)                                                             
(4, 998452.92)                                                             
(5, 249613.23)                                                            
(6, 62403.307)                                                            
(7, 15600.827)                                                            
(8, 3900.2067)                                                             
(9, 975.05168)                                                             
(10, 243.7629)                                                            
(11, 60.94073)                                                             
(12, 15.23518)                                                             
(13, 3.808796)                                                             
(14, 0.952199)                                                            
(15, 0.238050)                                                           
(16, 0.059512)*244m                                                        
(17, 0.014878)                                                          
(18, 0.003720) 
"""

import math

class LambertGrid:
    """LambertGrid Class"""
    def __init__(self, level, minx, maxx, miny, maxy, flip=False):
        # default y-axe direction is up
        # set self.flip = True to set y-axe direction to point down(this is what mercator webmap do) 
        self.flip = flip

        # constant variables
        self.pow_of_two = [1]
        for i in range(1, 20):
            self.pow_of_two.append(self.pow_of_two[i - 1] * 2)
        
        # earth variables
        self.earth_radius = 6378137
        # unit: square kilometers
        self.earth_area = 4 * math.pi * self.earth_radius * self.earth_radius / 1000000

        # how many small grids a big grid contains(along width/height)?
        self.grid_width = 256
        self.grid_height = 128
        
        self.max_val_index = self.grid_width * self.grid_height - 1

        # world original
        self.world_originalx = 0
        self.world_originaly = 0

        # world extent
        self.world_minx = -180.0
        self.world_maxx = 180.0

        self.world_miny = -1.0
        self.world_maxy = 1.0

        # small grid resolution at @level
        self.res_x = (self.world_maxx - self.world_minx) / self.pow_of_two[level + 1]
        self.res_y = (self.world_maxy - self.world_miny) / self.pow_of_two[level]

        # big grid width/height at @level
        self.extent_x = self.grid_width * self.res_x
        self.extent_y = self.grid_height * self.res_y

        # big grid extent
        self.minx = minx  # -180
        self.maxx = maxx  # 180
        self.miny = miny  # -1
        self.maxy = maxy  # 1

        # update big grid index
        self.update_boundary()
        # get big grid extent
        self.grids()


    def update_boundary(self):
        self.min_col = int(math.floor((self.minx - self.world_originalx) / self.extent_x))
        self.max_col = int(math.floor((self.maxx - self.world_originalx) / self.extent_x))

        if self.flip:
            self.min_row = int(math.floor((self.world_originaly - self.maxy) / self.extent_y))
            self.max_row = int(math.floor((self.world_originaly - self.miny) / self.extent_y))
        else:
            self.min_row = int(math.floor((self.miny - self.world_originaly) / self.extent_y))
            self.max_row = int(math.floor((self.maxy - self.world_originaly) / self.extent_y))

        self.total_grids = (self.max_col - self.min_col + 1) * (self.max_row - self.min_row + 1)
        return self.total_grids


    def grids(self):
        self.grid_list = {}

        for row in range(self.min_row, self.max_row + 1):
            for col in range(self.min_col, self.max_col + 1):
                key = '%d_%d' % (row, col)
                x0 = self.world_originalx + col * self.extent_x
                x1 = x0 + self.extent_x

                if self.flip:
                    y1 = self.world_originaly - row * self.extent_y
                    y0 = y1 - self.extent_y
                else:
                    y0 = self.world_originaly + row * self.extent_y
                    y1 = y0 + self.extent_y

                self.grid_list[key] = [x0, x1, y0, y1]

        return self.grid_list
    

    def grid_start_row_col(self):
        minrow = 100000000
        mincol = minrow
        for k in self.grid_list:
            row, col = k.split('_')
            row = int(row)
            col = int(col)
            if row < minrow:
                minrow = row
            if col < mincol:
                mincol = col
        return minrow, mincol


    def fine_grid(self, k):
        fine_grids = []
        ext = self.grid_list[k]

        # a grid contains grid.grid_width * grid.grid_height small grids
        for row in range(0, self.grid_height):
            for col in range(0, self.grid_width):
                # calculate small grid extent
                xx = ext[0] + col * self.res_x
                if self.flip:
                    yy = ext[3] - row * self.res_y
                    extent = [xx, xx + self.res_x, yy - self.res_y, yy]
                else:
                    yy = ext[2] + row * self.res_y
                    extent = [xx, xx + self.res_x, yy, yy + self.res_y]

                grid = {'idx': row * self.grid_width + col, 'extent': extent}
                fine_grids.append(grid)
    
        return fine_grids


    def grid_area(self, level):
        if level == 0:
            return self.earth_area / 2.0
        else:
            return self.grid_area(level - 1) / 4.0
        
    def grid_coordinate(self, row, col, srow, scol):
        x0 = self.world_originalx + col * self.extent_x
        xx = x0 + (scol + 0.5) * self.res_x

        if self.flip:
            y1 = self.world_originaly - row * self.extent_y
            y0 = y1 - self.extent_y
            yy = y0 - srow * self.res_y
            yy = yy - 0.5 * self.res_y
        else:
            y0 = self.world_originaly + row * self.extent_y
            yy = y0 + (srow + 0.5) * self.res_y
            
        return [xx, yy]