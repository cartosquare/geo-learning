--[[
/***************************************************************************
 opts
                                 utility
 parse options fro command line 
                              -------------------
        begin                : 2016-11-3
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
--]]

local M = { }

function M.parse(arg)
   local cmd = torch.CmdLine()
   cmd:text()
   cmd:text('GeoLearning Training script')
   cmd:text()
   cmd:text('Options:')
    ------------ General options --------------------
   cmd:option('-trainSet',  'data/train.t7',    'Path to training dataset')
   cmd:option('-testSet',   'data/test.t7',     'Path to test dataset')
   cmd:option('-r',   'r3',     'Can be: r1 | r2 | r3 | r4, grid resolution(meters per pixel)')
   cmd:option('-gridSize',   256,     'we store grid_size * grid_size in a grid layer')
   cmd:option('-gridList',   '',     'grid list for training')
   ------------ Fetch train test options --------------------
   cmd:option('-buffer',    12,         'how many nearby grid to included to compute')
   cmd:option('-features',       '',    'features to learn, seperated by space')
   ------------- Training options --------------------
   cmd:option('-nEpochs',         10,       'Number of total epochs to run')
   cmd:option('-batchSize',       1,      'mini-batch size (1 = pure stochastic)')
   ------------- Checkpointing options ---------------
   cmd:option('-save',            'checkpoints', 'Directory in which to save checkpoints')
   ---------- Optimization options ----------------------
   cmd:option('-LR',              0.1,   'initial learning rate')
   cmd:option('-momentum',        0.9,   'momentum')
   cmd:option('-weightDecay',     1e-4,  'weight decay')
   cmd:text()

   local opt = cmd:parse(arg or {})
   return opt
end

return M
