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
from osgeo import gdal
gdal.UseExceptions()

class RasterLayer:
    """RasterLayer Class"""
    def __init__(self):
        self.success = False

    def __del__(self):
        # clean
        self.datasource = None

    def open(self, src, band, format):
        # open raster layer
        try:
            self.datasource = gdal.Open(src)
        except RuntimeError, e:
            print 'Unable to open %s' % (src)
            self.success = False
            return self.success

        self.geo_transform = self.datasource.GetGeoTransform()
        self.extent = [geo_transform[0], geo_transform[0] + geo_transform[1] * self.datasource.RasterXSize, geo_transform[3] + geo_transform[5] * self.datasource.RasterYSize, geo_transform[3]]
        print extent

        try:
            self.layer = self.datasource.GetRasterBand(band)
        except RuntimeError, e:
            print 'Band ( %i ) not found' % band
            self.success = False
            return self.success
        
        stats = self.layer.GetStatistics(True, True)
        if stats is not None:
            print "[ STATS ] =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (stats[0], stats[1], stats[2], stats[3])
        
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
        data = layer.ReadAsArray(x_offset, y_offset, x_size, y_size)
        return self.data

    def statistic(self, extent):
        if not self.success:
            print('layer is not opened correctly')
            return

        data = self.spatialQuery(extent)
        if data is None:
            grid_val = 0
        else:
            data = data.astype(numpy.float)
            grid_val = numpy.average(data)
        return grid_val