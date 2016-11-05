# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Grid
                                 grid defination
 general grid defination and related operations
                              -------------------
        begin                : 2016-11-3
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
 We split raster/vector data into small grids. 
 To efficiently organize these small grids, we merge small grids into big grids. 
 We use google's protobuf format to define big grids, which is called GridData, you can refere protoc/grid_data.protoc for detail.

 This class defines the spatial info and spatial operations(including giving an extent, calculating how many big grids and small grids within it)

The most important spatial info about Grid is grid resolution and grid size,
grid resolution means how many meters a small grid represents, and grid size defines how many small grid(along width and height) a big grid contains.
"""

class Grid:
    """Grid Class"""
    def __init__(self, res, minx, maxx, miny, maxy):
        # how many small grids a big grid contains(along width/height)?
        self.grid_size = 256
        # resolution align names
        self.res_map = {
            # following resolutions can match to web map's resolutions
            # for example, in web map level 18, the extent of a tile is 152.8740565703125 meters
            'web12': 9783.9396205,
            'web13': 4891.96981025,
            'web14': 2445.984905125,
            'web15': 1222.9924525625,
            'web16': 611.49622628125,
            'web17': 305.748113140625,
            'web18': 152.8740565703125,
            'web19': 76.437028285156352,

            # following resolutions is some general resolutions
            'r100': 100,
            'r150': 150,
            'r200': 200,
            'r250': 250,
            'r500': 500,
            'r1000': 1000
        }

        # world original in mercator projection
        self.world_originalx = -20037508.342787
        self.world_originaly = 20037508.342787

        self.res = self.res_map[res]
        self.extent = self.res * self.grid_size
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy

        self.update_boundary()
        self.grids()

    def update_boundary(self):
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

        # a grid contains grid.grid_size * grid.grid_size small grids
        # list small girds in col-major(because column index changes first)
        for row in range(0, self.grid_size):
            for col in range(0, self.grid_size):
                # calculate small grid extent
                xx = ext[0] + row * self.res
                yy = ext[3] - col * self.res
                extent = [xx, xx + self.res, yy - self.res, yy]
                grid = {'idx': row * self.grid_size + col, 'extent': extent}
                fine_grids.append(grid)
    
        return fine_grids
