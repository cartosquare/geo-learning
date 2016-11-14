# -*- coding: utf-8 -*-

"""
/***************************************************************************
 LambertGrid
                                 lambert grid defination
 general grid defination and related operations
                              -------------------
        begin                : 2016-11-3
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

The most important spatial info about Grid is grid resolution and grid size,
grid resolution means how many meters a small grid represents, and grid size defines how many small grid(along width and height) a big grid contains.
"""
import math

class LambertGrid:
    """LambertGrid Class"""
    def __init__(self, level, minx, maxx, miny, maxy):
        # constant variables
        self.pow_of_two = [1]
        for i in range(1, 20):
            self.pow_of_two.append(self.pow_of_two[i - 1] * 2)
        
        # earth variables
        self.earth_radius = 6378137
        # unit: square kilometers
        self.earth_area = 4 * math.pi * self.earth_radius * self.earth_radius / 1000000

        # how many small grids a big grid contains(along width/height)?
        self.grid_size_x = 128
        self.grid_size_y = 256
        
        self.max_val_index = self.grid_size_x * self.grid_size_y - 1

        # left-upper corner as world original
        self.world_originalx = -180.0
        self.world_remotex = 180.0

        self.world_originaly = 1.0
        self.world_remotey = -1.0

        # small grid resolution at @level
        self.res_x = (self.world_remotex - self.world_originalx) / self.pow_of_two[level + 1]
        self.res_y = (self.world_originaly - self.world_remotey) / self.pow_of_two[level]

        # big grid width/height at @level
        self.extent_x = self.grid_size_x * self.res_x
        self.extent_y = self.grid_size_y * self.res_y

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
        self.min_ix = int((self.minx - self.world_originalx) / self.extent_x)
        self.min_iy = int((self.world_originaly - self.maxy) / self.extent_y)

        self.max_ix = int((self.maxx - self.world_originalx) / self.extent_x)
        self.max_iy = int((self.world_originaly - self.miny) / self.extent_y)

        self.total_grids = (self.max_ix - self.min_ix + 1) * (self.max_iy - self.min_iy + 1)
        return self.total_grids


    def grids(self):
        self.grid_list = {}
        for row in range(self.min_ix, self.max_ix + 1):
            for col in range(self.min_iy, self.max_iy + 1):
                key = '%d-%d' % (row, col)
                x0 = self.world_originalx + row * self.extent_x
                x1 = x0 + self.extent_x

                y0 = self.world_originaly - col * self.extent_y
                y1 = y0 - self.extent_y

                self.grid_list[key] = [x0, x1, y1, y0]

        return self.grid_list
    

    def grid_origin_index(self):
        minx = 100000000
        miny = minx
        for k in self.grid_list:
            x, y = k.split('-')
            x = int(x)
            y = int(y)
            if x < minx:
                minx = x
            if y < miny:
                miny = y
        return minx, miny


    def fine_grid(self, k):
        fine_grids = []
        ext = self.grid_list[k]

        # a grid contains grid.grid_size_x * grid.grid_size_y small grids
        # list small girds in col-major(because column index changes first)
        for row in range(0, self.grid_size_x):
            for col in range(0, self.grid_size_y):
                # calculate small grid extent
                xx = ext[0] + row * self.res_x
                yy = ext[3] - col * self.res_y
                extent = [xx, xx + self.res_x, yy - self.res_y, yy]
                grid = {'idx': row * self.grid_size_y + col, 'extent': extent}
                fine_grids.append(grid)
    
        return fine_grids


    def grid_area(self, level):
        if level == 0:
            return self.earth_area / 2.0
        else:
            return self.grid_area(level - 1) / 4.0
        