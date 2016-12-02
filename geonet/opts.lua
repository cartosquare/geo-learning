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
   cmd:option('-gridWidth',   256,     'we store gridWidth * gridHeight in a grid layer')
   cmd:option('-gridHeight',  128,     'we store gridWidth * gridHeight in a grid layer')
   cmd:option('-gridList',   '',     'grid list for training')
   cmd:option('-useGPU',   0,     'use gpu or not')
   ------------ Fetch train test options --------------------
   cmd:option('-buffer',    12,         'how many nearby grid to included to compute')
   cmd:option('-features',       '',    'features to learn, seperated by space')
   cmd:option('-label',     '', 'label data')
   cmd:option('-featDir',       'data/',    'directory that contains all the features')
   ------------- Training options --------------------
   cmd:option('-nEpochs',         10,       'Number of total epochs to run')
   cmd:option('-batchSize',       1,      'mini-batch size (1 = pure stochastic)')
   ------------- Checkpointing options ---------------
   cmd:option('-save',            'checkpoints', 'Directory in which to save checkpoints')
   ---------- Optimization options ----------------------
   cmd:option('-LR',              0.1,   'initial learning rate')
   cmd:option('-LRD',        0,   'learning Rate Decay')
   cmd:text()

   local opt = cmd:parse(arg or {})
   return opt
end

return M
