# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Grid
                                 grid defination
 general grid operations
                              -------------------
        begin                : 2016-11-3
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
"""
class Grid:
    """Grid Class"""
    def __init__(self, res, minx, maxx, miny, maxy):
        self.grid_size = 256
        self.res_map = {
            'r1': 305.748113140625,
            'r2': 38.21851414257813,
            'r3': 4.777314267822266,
            'r4': 0.597164283477783
        }
        self.world_originalx = -20037508.342787
        self.world_originaly = 20037508.342787

        self.res = self.res_map[res] * self.grid_size
        self.extent = self.res * self.grid_size
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy

        self.count()
        self.grids()

    def count(self):
        self.min_ix = int((self.minx - self.world_originalx) / self.extent)
        self.min_iy = int((self.world_originaly - self.maxy) / self.extent)

        self.max_ix = int((self.maxx - self.world_originalx) / self.extent)
        self.max_iy = int((self.world_originaly - self.miny) / self.extent)
    
        self.total_grids = (self.max_ix - self.min_ix + 1) * (self.max_iy - self.min_iy + 1)

        return self.total_grids

    def grids(self):
        self.grid_list = {}
        for row in range(self.min_ix, self.max_ix + 1):
            for col in range(self.min_iy, self.max_iy + 1):
                key = '%d-%d' % (row, col)
                x0 = self.world_originalx + row * self.extent
                y0 = self.world_originaly - col * self.extent
                self.grid_list[key] = [x0, x0 + self.extent, y0 - self.extent, y0]

        return self.grid_list

    def fine_grid(self, x0, y0):
        fine_grids = []
        for row in range(0, self.grid_size):
            fine_grids[row] = []
            for col in range(0, self.grid_size):
                xx = x0 + row * self.res
                yy = y0 - col * self.res

                fine_grids[row][col] = [xx, xx + self.res, yy, yy - self.res]

        return fine_grids
