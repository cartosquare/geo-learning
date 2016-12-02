# -*- coding: utf-8 -*-

"""
/***************************************************************************
 spatial smooth
                                 spatial smooth script
 to smooth spatial distribution
                              -------------------
        begin                : 2016-12-1
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
"""

import sqlite3
import geogrid.grid_data_pb2 as grid_data_pb2
from geogrid.feature_db import FeatureDB
from geogrid.lambert_grid import LambertGrid
from geogrid import proj_util
import argparse
import random
import math
from progressbar import *


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Feed data to grid.')
    parser.add_argument('db', metavar='db', type=str, help='source data file to read')
    parser.add_argument('-r', dest='resolution', type=str, help='resolution name')

    # parse arguments
    args = parser.parse_args()

    # open feature db
    feature_db = FeatureDB(args.db)
    grid_info = feature_db.queryGridInfo()
    grid_width = grid_info[3]
    grid_height = grid_info[4]
    print(grid_width, grid_height)
    extent = feature_db.queryLambertExtent()
    print 'extent(minx, maxx, miny, maxy)', extent

    grid = LambertGrid(int(args.resolution), extent[0], extent[1], extent[2], extent[3], grid_info[2])

    # slide window parameters/infos
    buffer = 4
    weight_sum = 0
    for i in range(-buffer, buffer + 1):
        for j in range(-buffer, buffer + 1):
            weight = 1.0 / (i * i + j * j + 1.0)
            weight_sum = weight_sum + weight
    print 'slide window weight sum', weight_sum


    # fetch grid data
    feature_db.queryByResolution('level' + args.resolution)
    row = feature_db.nextRow()
    griddata_list = {}
    while row is not None:
        griddata = grid_data_pb2.GridData.FromString(row[1])
        griddata_list[griddata.name] = griddata

        row = feature_db.nextRow()

    total_grids = len(griddata_list)
    print('#grids: ', total_grids)

    # strange grid value cutline
    bad_grid_value = 15

    # spatial smooth bad grids
    cnt = 0
    grid_cnt = 0
    for key in griddata_list:
        # parse data
        griddata = griddata_list[key]

        #print(griddata.name)
        z, x, y = griddata.name.split('_')
        x = int(x)
        y = int(y)

        grid_cnt = grid_cnt + 1
    
        layer = griddata.layers[0]
        num_keys = len(layer.keys)
        key_cnt = 0
        for i in range(0, num_keys):
            key_cnt = key_cnt + 1
            print('grid %d of %d, key %d of %d' % (grid_cnt, len(griddata_list), key_cnt, num_keys))

            idx = layer.keys[i]
            if idx < len(layer.values): # some grid may not be recorded
                if layer.values[idx] > bad_grid_value:
                    row = i / grid_width
                    col = i % grid_width
                    # global index of this sample
                    ox = x * grid_height + row
                    oy = y * grid_width + col
                    
                    for irow in range(-buffer, buffer + 1):
                        for icol in range(-buffer, buffer + 1):
                            n_ox = ox + irow
                            n_oy = oy + icol
                                
                            # global/relative index
                            n_x = int(math.floor(n_ox / grid_height))
                            n_ix = n_ox % grid_height

                            n_y = int(math.floor(n_oy / grid_width))
                            n_iy = n_oy % grid_width

                            # grid id
                            gid = z + '_' + str(n_x) + '_' + str(n_y)
                            new_grid_data = griddata_list[gid]

                            #grid_row = feature_db.queryByID(gid)
                            grid_idx = n_ix * grid_width + n_iy
                            #new_grid_data = grid_data_pb2.GridData.FromString(grid_row[1])

                            grid_layer = new_grid_data.layers[0]
                            grid_value_idx = grid_layer.keys[grid_idx]

                            weight = (1.0 / (irow * irow + icol * icol + 1.0)) / weight_sum
                            if grid_value_idx >= len(layer.values):
                                # todo: distance related calculated method
                                new_grid_value = layer.values[idx] * weight
                            else:
                                if irow == 0 and icol == 0:
                                    new_grid_value = layer.values[idx] * weight
                                else:
                                    new_grid_value = layer.values[idx] * weight + grid_layer.values[grid_value_idx]
                                #print grid_layer.values[grid_value_idx], ' -> ', new_grid_value

                            # update grid value
                            """
                            target_key = None
                            for key_idx in range(0, len(grid_layer.values)):
                                if new_grid_value == grid_layer.values[key_idx]:
                                    target_key = key_idx
                                    break
                            if target_key is None:
                                grid_layer.keys[grid_idx] = len(grid_layer.values)
                                grid_layer.values.append(new_grid_value)
                            else:
                                grid_layer.keys[grid_idx] = target_key
                            """
                            grid_layer.keys[grid_idx] = len(grid_layer.values)
                            grid_layer.values.append(new_grid_value)

                    cnt = cnt + 1
                    #pbar.update(cnt)
    #pbar.finish()

    # refresh feature db
    print 'total processed count', cnt
    print 'saving...'
    for key in griddata_list:
        griddata = griddata_list[key]
        proto_str = griddata.SerializeToString()
        feature_db.upsert(key, args.resolution, proto_str)
        feature_db.commit()
    
    print 'finish!'