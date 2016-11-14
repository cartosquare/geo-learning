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
import proj_util
from lambert_gird import LambertGrid as Grid
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
        self.feature_table = None
        self.output_dir = None

    def openLayer(self, opts):
        if opts.type == 'vector':
            layer = VectorLayer()

            if opts.layer is None:
                layer_loc = opts.ilayer
            else:
                layer_loc = opts.layer
            if not layer.open(opts.src, layer_loc, opts.format, opts.filter):
                return None

            if (opts.srs == 'epsg:4326'):
                layer.setScale(1000000.0)
            else:
                # opts.srs == 'epsg:3857'
                layer.setScale(1000.0)
            print('scale', layer.scale)
        else:
            layer = RasterLayer()
            if not layer.open(opts.src, opts.ilayer, opts.format):
                return None
        
        # set statistic mode
        layer.setStatisticMethod(opts.method, opts.cell_value)

        return layer

    def openSource(self, opts):
        # open layer
        self.layer = self.openLayer(opts)

        # update extent if specied
        self.extent = [
                self.layer.extent[0] if opts.xmin is None else opts.xmin, 
                self.layer.extent[1] if opts.xmax is None else opts.xmax, 
                self.layer.extent[2] if opts.ymin is None else opts.ymin, 
                self.layer.extent[3] if opts.ymax is None else opts.ymax
            ]

        # transform coordinates
        self.srs = opts.srs
        if (opts.srs == 'epsg:4326'):
            [xmin, ymin] = proj_util.lonlat2lambert([self.extent[0], self.extent[2]])
            [xmax, ymax] = proj_util.lonlat2lambert([self.extent[1], self.extent[3]])
        else:
            # opts.srs == 'epsg:3857'
            [xmin, ymin] = proj_util.webmercator2lonlat([self.extent[0], self.extent[2]])
            [xmax, ymax] = proj_util.webmercator2lonlat([self.extent[1], self.extent[3]])
            [xmin, ymin] = proj_util.lonlat2lambert([xmin, ymin])
            [xmax, ymax] = proj_util.lonlat2lambert([xmax, ymax])

        self.lambert_extent = [xmin, xmax, ymin, ymax]
        print('lambert extent: ', self.lambert_extent)

        # calculate grids
        self.grids = Grid(self.resolution, xmin, xmax, ymin, ymax)
        self.total_fine_grids = self.grids.total_grids * self.grids.grid_size_x * self.grids.grid_size_y
        print "total grids: %d, %d" % (self.grids.total_grids, self.total_fine_grids)

        self.open_src_success = True
        return self.open_src_success


    def openDest(self, args):
        print 'output', args.output_format

        if args.output_format == 'sqlite3':
            # open feature db, will create if not exist
            self.feature_table = FeatureDB(args.output)
        else:
            self.output_dir = args.output
            if not os.path.exists(self.output_dir):
                os.mkdir(self.output_dir)

        self.open_dest_success = True
        return self.open_dest_success


    def is_ok(self):
        if not self.open_src_success or not self.open_dest_success:
            print('please open src and dest data first!')
            return False
        else:
            return True


    def updateMetas(self):
        if not self.is_ok():
            return

        # write metas 
        date = datetime.datetime.now()
        if self.feature_table is not None:
            self.feature_table.upsertMeta('minx', self.extent[0])
            self.feature_table.upsertMeta('maxx', self.extent[1])
            self.feature_table.upsertMeta('miny', self.extent[2])
            self.feature_table.upsertMeta('maxy', self.extent[3])
            self.feature_table.upsertMeta('lambert_minx', self.lambert_extent[0])
            self.feature_table.upsertMeta('lambert_maxx', self.lambert_extent[1])
            self.feature_table.upsertMeta('lambert_miny', self.lambert_extent[2])
            self.feature_table.upsertMeta('lambert_maxy', self.lambert_extent[3])
            self.feature_table.upsertMeta('last_modified', date.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            meta_file = os.path.join(self.output_dir, 'metas.txt')
            f = open(meta_file, 'w')
            f.write('minx,%f\n' % (self.extent[0]))
            f.write('maxx,%f\n' % (self.extent[1]))
            f.write('miny,%f\n' % (self.extent[2]))
            f.write('maxy,%f\n' % (self.extent[3]))
            f.write('lambert_minx,%f\n' % (self.lambert_extent[0]))
            f.write('lambert_maxx,%f\n' % (self.lambert_extent[1]))
            f.write('lambert_miny,%f\n' % (self.lambert_extent[2]))
            f.write('lambert_maxy,%f\n' % (self.lambert_extent[3]))
            f.write('last_modified,%s\n' % (date.strftime("%Y-%m-%d %H:%M:%S")))
            f.close()


    def makeGrid(self, k, layer):
        # we store grid data in protobuf format
        grid_data = grid_data_pb2.GridData()
        grid_data.name = 'level' + str(self.resolution) + '-' + k
        
        # add a layer to grid data
        grid_layer = grid_data.layers.add()
        grid_layer.version = 2
        grid_layer.name = self.layer.name

        for find_grid in self.grids.fine_grid(k):
            # do statistic of this small grid
            ext = find_grid['extent']
            # transform coordinates
            if (self.srs == 'epsg:4326'):
                [xmin, ymin] = proj_util.lambert2lonlat([ext[0], ext[2]])
                [xmax, ymax] = proj_util.lambert2lonlat([ext[1], ext[3]])
            else:
                # opts.srs == 'epsg:3857'
                [xmin, ymin] = proj_util.lambert2lonlat([ext[0], ext[2]])
                [xmax, ymax] = proj_util.lambert2lonlat([ext[1], ext[3]])
                [xmin, ymin] = proj_util.lonlat2webmercator([xmin, ymin])
                [xmax, ymax] = proj_util.lonlat2webmercator([xmax, ymax])

            grid_val = layer.statistic([xmin, xmax, ymin, ymax])
            if grid_val is None:
                # this grid has no data, indicate that it's not calculated
                # because we have at most self.grids.grid_size * self.grids.grid_size small grids in
                # a big grid, the index to value could not exceed self.grids.grid_size * self.grids.grid_size - 1, here we use self.grids.max_val_index = self.grids.grid_size * self.grids.grid_size to represent that this grid has no data
                grid_layer.keys.append(self.grids.max_val_index + 1)
            else:
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
        # save to db
        proto_str = grid_data.SerializeToString()
        if self.feature_table is not None:
            self.feature_table.upsert(grid_data.name, self.resolution, proto_str)
        else:
            grid_path = os.path.join(self.output_dir, grid_data.name)
            f = open(grid_path, 'wb')
            f.write(proto_str)
            f.close()    


    def make(self):
        if not self.is_ok():
            return
        
        # use a progress bar to show the progress of generating grids
        cnt = 0 
        # widgets = [Percentage(), Bar('>'), ' ', Timer(), BouncingBar(), ETA(), ' ', ReverseBar('<')]
        widgets = [Bar('>'), ' ', Percentage(), ' ', Timer(), ' ', ETA()]
        pbar = ProgressBar(widgets=widgets, maxval=self.grids.total_grids).start()

        # generating all the grids
        for k in self.grids.grid_list:
            self.makeGrid(k, self.layer)

            # update progress bar
            cnt = cnt + 1
            pbar.update(cnt)

        # finish, do not forget to commit
        if self.feature_table is not None:
            self.feature_table.commit()

        pbar.finish()
        return True