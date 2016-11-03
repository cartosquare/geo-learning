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
import argparse
import numpy
import scipy.misc

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Visualize Feature')
    parser.add_argument('db', metavar='db', type=str, help='source data file to read')
    parser.add_argument('-o', dest='output', type=str, help='output image file')
    parser.add_argument('-r', dest='resolution', type=str, help='resolution r1-r4')
    parser.add_argument('--gridSize', dest='grid_size', type=int, help='grid size, default to 256')
    parser.add_argument('--xmin', dest='xmin', type=float, help="x min")
    parser.add_argument('--xmax', dest='xmax', type=float, help="x max")
    parser.add_argument('--ymin', dest='ymin', type=float, help="y min")
    parser.add_argument('--ymax', dest='ymax', type=float, help="y max")

    # parse arguments
    args = parser.parse_args()
    print args

    db_path = args.db
    db = sqlite3.connect(db_path)

    r = args.resolution
    output = args.output
    if args.output is None:
        output = 'output.jpg'
    else:
        output = args.output

    if args.grid_size is None:
        grid_size = 256
    else:
        grid_size = args.grid_size

    print('grid size', grid_size)

    grids = Grid(r, args.xmin, args.xmax, args.ymin, args.ymax)
    dim = grids.total_grids * grids.grid_size
    print ('dim', dim)
    img_arr = numpy.zeros((dim, dim))

    # find top-left grid Index
    minx = 100000000
    miny = 100000000
    for k in grids.grid_list:
        x, y = k.split('-')
        x = int(x)
        y = int(y)
        if x < minx:
            minx = x
        if y < miny:
            miny = y
    print('min, max', minx, miny)

    pmin = 1000000
    pmax = -pmin
    for k in grids.grid_list:
        grid_name = r + '-' + k
        cursor = db.execute("SELECT ID, DATA from feature WHERE ID = '%s'" % (grid_name))
        for row in cursor:
            x, y = k.split('-')
            x = int(x)
            y = int(y)
            x_offset = grid_size * (x - minx)
            y_offset = grid_size * (y - miny)

            # parse data
            griddata = grid_data_pb2.GridData.FromString(row[1])

            layer = griddata.layers[0]
            for i in range(0, len(layer.keys)):
                idx = layer.keys[i]

                row = i / grid_size
                col = i % grid_size

                val = layer.values[idx]
                img_arr[row + x_offset][col + y_offset] = val
                if val < pmin:
                    pmin = val
                if val > pmax:
                    pmax = val


    #scipy.misc.imsave(output, img_arr)
    print ('pixel min max', pmin, pmax)
    #scipy.misc.toimage(img_arr, cmin=pmin, cmax=...).save(output)
    scipy.misc.toimage(img_arr, cmin=0.0, cmax=pmax).save('outfile.jpg')