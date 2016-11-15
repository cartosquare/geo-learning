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
from lambert_gird import LambertGrid as Grid
import grid_data_pb2
from feature_db import FeatureDB
import argparse
import numpy
import scipy.misc

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Visualize Feature')
    parser.add_argument('db', metavar='db', type=str, help='source data file to read')
    parser.add_argument('-o', dest='output', type=str, help='output image file')
    parser.add_argument('-r', dest='resolution', type=int, help='resolution level')
    parser.add_argument('-c', dest='constant', type=int, help='constant light')
    parser.add_argument('-g', dest='grid', type=int, help='display grid or not')

    # parse arguments
    args = parser.parse_args()
    if args.output is None:
        args.output = 'output.jpg'
    if args.resolution is None:
        print 'please specify -r option'
        exit(0)
    if args.constant is None:
        args.constant = 1
    if args.grid is None:
        if args.constant == 1:
            args.grid = 1
        else:
            args.grid = 0

    feature_db = FeatureDB(args.db)
    extent = feature_db.queryLambertExtent()
    print 'extent(minx, maxx, miny, maxy)', extent

    # draw a big image contains all the grids
    grids = Grid(args.resolution, extent[0], extent[1], extent[2], extent[3])
    # big image's dimension
    height = (grids.max_row - grids.min_row + 1) * grids.grid_height
    width = (grids.max_col - grids.min_col + 1) * grids.grid_width
    print(grids.max_row, grids.min_row)
    print(grids.max_col, grids.min_col)
    print('output image dim', width, height)
    img_arr = numpy.zeros((height, width))

    # find start row col
    minrow, mincol = grids.grid_start_row_col()

    pmin = 1000000
    pmax = -pmin
    print(len(grids.grid_list))

    for k in grids.grid_list:
        grid_name = 'level' + str(args.resolution) + '-' + k
        row, col = k.split('-')
        row = int(row)
        col = int(col)
        bk_val = 0
        if row % 2 == 0:
            if col % 2 == 1:
                bk_val = 0
            else:
                bk_val = 20
        else:
            if col % 2 == 1:
                bk_val = 40
            else:
                bk_val = 60

        griddata = feature_db.queryByID(grid_name)
        if griddata is not None:
            row_offset = grids.grid_height * (row - minrow)
            col_offset = grids.grid_width * (col - mincol)

            # parse data
            griddata = grid_data_pb2.GridData.FromString(griddata[1])

            layer = griddata.layers[0]
            for irow in range(0, grids.grid_height):
                for icol in range(0, grids.grid_width):
                    idx = layer.keys[irow * grids.grid_width + icol]
                    if idx > grids.max_val_index:
                        img_arr[irow + row_offset][icol + col_offset] = bk_val
                        continue

                    val = layer.values[idx]
                    if val > 0:
                        if args.constant == 1:
                            img_arr[irow + row_offset][icol + col_offset] = 255
                        else:
                            img_arr[irow + row_offset][icol + col_offset] = val
                    else:
                        img_arr[irow + row_offset][icol + col_offset] = bk_val

                    if val < pmin:
                        pmin = val
                    if val > pmax:
                        pmax = val
    
    print ('pixel min max', pmin, pmax)
    if args.constant:
        scipy.misc.imsave(args.output, img_arr)
    else:
        scipy.misc.toimage(img_arr, cmin=pmin, cmax=pmax).save(args.output)