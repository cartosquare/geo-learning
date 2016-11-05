# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Mesher
                                 Mesher
 Mesher vector/raster data
                              -------------------
        begin                : 2016-11-4
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
"""
import os
import sys
import math
from grid import Grid
import grid_data_pb2
from feature_db import FeatureDB
from vector_layer import VectorLayer
from raster_layer import RasterLayer
from progressbar import *


class Mesher:
    """Mesher Class"""
    def __init__(self, resolution):
        self.open_src_success = False
        self.open_dest_success = False
        self.resolution = resolution


    def openSource(self, opts):
        # open layer
        if opts.type == 'vector':
            self.layer = VectorLayer()
        else:
            self.layer = RasterLayer()
        if not self.layer.open(opts.src, opts.ilayer, opts.format):
            return open_src_success

        # update extent if specied
        self.extent = [
                self.layer.extent[0] if opts.xmin is None else opts.xmin, 
                self.layer.extent[1] if opts.xmax is None else opts.xmax, 
                self.layer.extent[2] if opts.ymin is None else opts.ymin, 
                self.layer.extent[3] if opts.ymax is None else opts.ymax
            ]

        # calculate grids
        self.grids = Grid(self.resolution, self.extent[0], self.extent[1], self.extent[2], self.extent[3])
        self.total_grids = self.grids.total_grids * self.grids.grid_size * self.grids.grid_size
        print "total grids: %d, %d" % (self.grids.total_grids, self.total_grids)

        self.open_src_success = True
        return self.open_src_success


    def openDest(self, path):
        # open feature db, will create if not exist
        self.feature_table = FeatureDB(path)

        # create table if not exists
        self.feature_table.createTable()

        self.open_dest_success = True
        return self.open_dest_success

    def make(self):
        if not self.open_src_success or not self.open_dest_success:
            print('please open src and dest data first!')
            return False

        # use a progress bar to show the progress of generating grids
        cnt = 0 
        # widgets = [Percentage(), Bar('>'), ' ', Timer(), BouncingBar(), ETA(), ' ', ReverseBar('<')]
        widgets = [Bar('>'), ' ', Percentage(), ' ', Timer(), ' ', ETA()]
        pbar = ProgressBar(widgets=widgets, maxval=self.total_grids).start()
        for k in self.grids.grid_list:
            # we store grid data in protobuf format
            grid_data = grid_data_pb2.GridData()
            grid_data.name = self.resolution + '-' + k
        
            # add a layer to grid data
            grid_layer = grid_data.layers.add()
            grid_layer.version = 2
            grid_layer.name = self.layer.name

            count = 0
            for find_grid in self.grids.fine_grid(k):
                # do statistic of this small grid
                grid_val = self.layer.statistic(find_grid['extent'])

                # find whether this grid value is already recorded
                target = -1
                for i in range(0, len(grid_layer.values)):
                    if abs(grid_val - grid_layer.values[i]) < 0.00001:
                        target = i

                # make sure that grids are in the right order
                if (find_grid['idx'] != len(grid_layer.keys)):
                    print 'grids index are broken!'

                # add small grid value to grid layer
                if target == -1:
                    # if not recorded, we should record the key and value
                    grid_layer.keys.append(len(grid_layer.values))
                    grid_layer.values.append(grid_val)
                else:
                    # if already recorded, only add the key to save space
                    grid_layer.keys.append(target)

                # update progress bar
                cnt = cnt + 1
                pbar.update(cnt)
            # save to db
            proto_str = grid_data.SerializeToString()
            self.feature_table.upsert(grid_data.name, self.resolution, proto_str)
        
        # finish, do not forget to commit
        self.feature_table.commit()
        pbar.finish()
        return True

