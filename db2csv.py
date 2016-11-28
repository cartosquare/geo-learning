# -*- coding: utf-8 -*-

"""
/***************************************************************************
 vis_feature
                                 visualize feature
render an image of the feature
                              -------------------
        begin                : 2016-11-28
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
"""

import sqlite3
from geogrid.lambert_grid import LambertGrid as Grid
import geogrid.grid_data_pb2 as grid_data_pb2
from geogrid.feature_db import FeatureDB
from geogrid import proj_util
import argparse
import numpy
import scipy.misc

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Visualize Feature')
    parser.add_argument('db', metavar='db', type=str, help='source data file to read')
    parser.add_argument('-o', dest='output', type=str, help='output image file')
    parser.add_argument('-r', dest='resolution', type=int, help='resolution level')
    parser.add_argument('-n', dest='nodata', type=int, help='no data value')

    # parse arguments
    args = parser.parse_args()
    if args.output is None:
        args.output = 'output.csv'
    if args.resolution is None:
        print 'please specify -r option'
        exit(0)
    if args.nodata is None:
        args.nodata = 0

    f = open(args.output, 'w')
    f.write('lon,lat,row,col,irow,icol,val\n')

    feature_db = FeatureDB(args.db)
    extent = feature_db.queryLambertExtent()
    print 'extent(minx, maxx, miny, maxy)', extent

    gridInfo = feature_db.queryGridInfo()
    print 'grid info', gridInfo

    grids = Grid(args.resolution, extent[0], extent[1], extent[2], extent[3], gridInfo[2])
    
    for k in grids.grid_list:
        grid_name = 'level' + str(args.resolution) + '_' + k
        print('process subgrid', grid_name)
        row, col = k.split('_')
        row = int(row)
        col = int(col)

        griddata = feature_db.queryByID(grid_name)
        if griddata is not None:
            # parse data
            griddata = grid_data_pb2.GridData.FromString(griddata[1])

            layer = griddata.layers[0]
            for irow in range(0, grids.grid_height):
                for icol in range(0, grids.grid_width):
                    idx = layer.keys[irow * grids.grid_width + icol]

                    if idx > grids.max_val_index:
                        continue

                    val = layer.values[idx]
                    if val == args.nodata:
                        continue

                    coord = grids.grid_coordinate(row, col, irow, icol)
                    [lon, lat] = proj_util.lambert2lonlat(coord)
                    
                    f.write('%f,%f,%d,%d,%d,%d,%f\n' % (lon, lat, row, col, irow, icol, val))
    f.close()
    