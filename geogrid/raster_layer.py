# -*- coding: utf-8 -*-

"""
/***************************************************************************
 raster_layer
                                 raster layer
 operation about raster layers
                              -------------------
        begin                : 2016-11-4
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
"""

import os
import sys
import numpy
from osgeo import gdal
gdal.UseExceptions()

class RasterLayer:
    """RasterLayer Class"""
    def __init__(self):
        self.success = False
        self.method = 'count'
        self.user_data = None


    def __del__(self):
        # clean
        self.datasource = None


    def setStatisticMethod(self, method, user_data):
        self.method = method
        self.user_data = user_data


    def open(self, src, band, format):
        # open raster layer
        try:
            self.datasource = gdal.Open(src)
        except RuntimeError, e:
            print 'Unable to open %s' % (src)
            self.success = False
            return self.success

        self.geo_transform = self.datasource.GetGeoTransform()
        self.extent = [self.geo_transform[0], self.geo_transform[0] + self.geo_transform[1] * self.datasource.RasterXSize, self.geo_transform[3] + self.geo_transform[5] * self.datasource.RasterYSize, self.geo_transform[3]]
        print self.extent

        try:
            self.layer = self.datasource.GetRasterBand(band)
        except RuntimeError, e:
            print 'Band ( %i ) not found' % band
            self.success = False
            return self.success
        
        stats = self.layer.GetStatistics(True, True)
        if stats is not None:
            print "[ STATS ] =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (stats[0], stats[1], stats[2], stats[3])
        
        self.name = 'band %d' % (band)
        self.success = True
        return self.success

    def spatialQuery(self, extent):
        if not self.success:
            print('layer is not opened correctly')
            return

        # statistic for raster layer
        x_offset = int((extent[0] - self.geo_transform[0]) / self.geo_transform[1])
        y_offset = int((extent[3] - self.geo_transform[3]) / self.geo_transform[5])
        x_size = int((extent[1] - extent[0]) / self.geo_transform[1] + 0.5)
        y_size = int((extent[2] - extent[3]) / self.geo_transform[5] + 0.5)

        # skip nonsense queries
        if x_offset >= self.datasource.RasterXSize or y_offset >= self.datasource.RasterYSize:
            return None
        if x_offset + x_size < 0 or y_offset + y_size < 0:
            return None

        # limit query extent to the datasource extent
        # TODO: When raster data are feed in as many seperated files,
        # the values of grids lies on the boundary may not accuracy!
        # you can merge seperated files into larger one to avoid this issue,
        # but programming methods should be taken to deal with it!!!
        if x_offset + x_size > self.datasource.RasterXSize:
            x_size = self.datasource.RasterXSize - x_offset

        if y_offset + y_size > self.datasource.RasterYSize:
            y_size = self.datasource.RasterYSize - y_offset

        if x_offset < 0:
            x_offset = 0

        if y_offset < 0:
            y_offset = 0

        # then, query
        data = self.layer.ReadAsArray(x_offset, y_offset, x_size, y_size)
        return data

    def statistic(self, extent):
        if not self.success:
            print('layer is not opened correctly')
            return

        data = self.spatialQuery(extent)
        if data is None:
            return None
        
        if self.method == 'sum':
            return self.sum(data)
        elif self.method == 'average':
            return self.average(data)
        elif self.method == 'count':
            return self.count(data, self.user_data)
        elif self.method == 'frequency':
            return self.frequency(data, self.user_data)
        else:
            print 'unsupport method %s' % (self.method)
            return None
    

    # average of all cell values
    def average(self, data):
        data = data.astype(numpy.float)
        grid_val = numpy.average(data)
        return grid_val
    

    # sum of all cell values
    def sum(self, data):
        data = data.astype(numpy.float)
        grid_val = numpy.sum(data)
        return grid_val


    # appear times of specified cell value
    def count(self, data, val):
        data = data.astype(numpy.int)
        (row, col) = data.shape

        grid_val = 0
        for i in range(0, row):
            for j in range(0, col):
                if data[i][j] == val:
                    grid_val = grid_val + 1

        return grid_val
    

    # appear times divide total times of specified cell value
    def frequency(self, data, val):
        grid_val = float(self.count(data, val))
        total_val = data.shape[0] * data.shape[1]

        return (grid_val / total_val)