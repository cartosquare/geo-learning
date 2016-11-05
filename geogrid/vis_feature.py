# -*- coding: utf-8 -*-

"""
/***************************************************************************
 vis_feature
                                 visualize feature
render an image of the feature
                              -------------------
        begin                : 2016-11-3
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
"""

import sqlite3
from grid import Grid
import grid_data_pb2
from feature_db import FeatureDB
import argparse
import numpy
import scipy.misc

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Visualize Feature')
    parser.add_argument('db', metavar='db', type=str, help='source data file to read')
    parser.add_argument('-o', dest='output', type=str, help='output image file')
    parser.add_argument('-r', dest='resolution', type=str, help='resolution')
    parser.add_argument('--xmin', dest='xmin', type=float, help="x min")
    parser.add_argument('--xmax', dest='xmax', type=float, help="x max")
    parser.add_argument('--ymin', dest='ymin', type=float, help="y min")
    parser.add_argument('--ymax', dest='ymax', type=float, help="y max")

    # parse arguments
    args = parser.parse_args()
    if args.output is None:
        args.output = 'output.jpg'
    if args.resolution is None:
        print 'please specify -r option'
        exit(0)

    feature_db = FeatureDB(args.db)

    # grid arrangement is col-major
    grids = Grid(args.resolution, args.xmin, args.xmax, args.ymin, args.ymax)
    height = (grids.max_ix - grids.min_ix + 1) * grids.grid_size
    width = (grids.max_iy - grids.min_iy + 1) * grids.grid_size

    print('output image dim', width, height)
    img_arr = numpy.zeros((width, height))

    # find top-left grid Index
    minx, miny = grids.grid_origin_index()
    print('minx, miny', minx, miny)

    pmin = 1000000
    pmax = -pmin
    for k in grids.grid_list:
        grid_name = args.resolution + '-' + k
        
        row = feature_db.queryByID(grid_name)
        if row is not None:
            x, y = k.split('-')
            x = int(x)
            y = int(y)
            col_offset = grids.grid_size * (x - minx)
            row_offset = grids.grid_size * (y - miny)

            # parse data
            griddata = grid_data_pb2.GridData.FromString(row[1])

            layer = griddata.layers[0]
            for xx in range(0, grids.grid_size):
                for yy in range(0, grids.grid_size):
                    idx = layer.keys[xx * grids.grid_size + yy]
                    val = layer.values[idx]
                    if val > 0:
                        # rearrange to row-major
                        img_arr[yy + row_offset][xx + col_offset] = 255
                    if val < pmin:
                        pmin = val
                    if val > pmax:
                        pmax = val


    scipy.misc.imsave(args.output, img_arr)
    print ('pixel min max', pmin, pmax)
    #scipy.misc.toimage(img_arr, cmin=pmin, cmax=...).save(output)
    #scipy.misc.toimage(img_arr, cmin=0.0, cmax=pmax).save(args.output)