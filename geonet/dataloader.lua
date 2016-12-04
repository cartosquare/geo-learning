--[[
/***************************************************************************
 dataloader
                                 load data and split into batchs
 data loader
                              -------------------
        begin                : 2016-12-03
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
--]]

require 'torch'
require 'math'


local M = {}
local DataLoader = torch.class('geonet.DataLoader', M)

function DataLoader:__init(opt)
    -- loading train/test sets
    print('loading trainset', opt.trainSet)
    self.trainset = torch.load(opt.trainSet)
    print('loading testset', opt.testSet)
    self.testset = torch.load(opt.testSet)

    self.nTrainSamples = self.trainset.data:size(1)
    self.nTestSamples = self.testset.data:size(1)
    self.nTrainSize = math.ceil(self.nTrainSamples / opt.batchSize)
    self.nTestSize = math.ceil(self.nTestSamples / opt.batchSize)

    print('#trainSamples', self.nTrainSamples)
    print('#trainSize', self.nTrainSize)
    print('#testSamples', self.nTestSamples)
    print('#testSize', self.nTestSize)

    self.nfeatures = self.trainset.data:size(2)
    
    self.batchSize = opt.batchSize
    self.useGPU = opt.useGPU
end

function DataLoader:trainSize()
    return self.nTrainSize
end

function DataLoader:testSize()
    return self.nTestSize
end

function DataLoader:normalize()
    -- normalize train/test: make data to have a mean of 0.0 and standard-deviation of 1.0
    mean = {} -- store the mean, to normalize the test set in the future
    stdv  = {} -- store the standard-deviation for the future
    for i = 1, self.nfeatures do -- over each channel
        mean[i] = self.trainset.data[{ {}, {i}, {}, {}  }]:mean() -- mean estimation
        print('Channel ' .. i .. ', Mean: ' .. mean[i])
        self.trainset.data[{ {}, {i}, {}, {}  }]:add(-mean[i]) -- mean subtraction
    
        stdv[i] = self.trainset.data[{ {}, {i}, {}, {}  }]:std() -- std estimation
        print('Channel ' .. i .. ', Standard Deviation: ' .. stdv[i])
        self.trainset.data[{ {}, {i}, {}, {}  }]:div(stdv[i]) -- std scaling
    end
    -- the same operation to test set
    for i = 1, self.nfeatures do -- over each channel
        self.testset.data[{ {}, {i}, {}, {}  }]:add(-mean[i]) -- mean subtraction    
        self.testset.data[{ {}, {i}, {}, {}  }]:div(stdv[i]) -- std scaling
    end
end

function DataLoader:trainBatch(nbatch)
    start_idx = self.batchSize * (nbatch - 1) + 1
    end_idx = self.batchSize * nbatch

    if end_idx > self.nTrainSamples then
        end_idx = self.nTrainSamples
    end

    batchInputs = torch.DoubleTensor(self.batchSize, self.nfeatures, 9, 9)
    batchLabels = torch.DoubleTensor(self.batchSize)
    local cnt = 0
    for s = start_idx, end_idx do
        cnt = cnt + 1

        batchInputs[cnt] = self.trainset.data[s]
        batchLabels[cnt] = self.trainset.label[s]
    end
    if cnt < self.batchSize then
        nremained = self.batchSize - cnt
        for ss = 1, nremained do
            cnt = cnt + 1

            batchInputs[cnt] = self.trainset.data[ss]
            batchLabels[cnt] = self.trainset.label[ss]
        end
    end

    return batchInputs, batchLabels
end

function DataLoader:validateBatch(nbatch)
    start_idx = self.batchSize * (nbatch - 1) + 1
    end_idx = self.batchSize * nbatch

    if end_idx > self.nTestSamples then
        end_idx = self.nTestSamples
    end

    batchInputs = torch.DoubleTensor(end_idx - start_idx + 1, self.nfeatures, 9, 9)
    batchLabels = torch.DoubleTensor(end_idx - start_idx + 1)
    local cnt = 0
    for s = start_idx, end_idx do
        cnt = cnt + 1

        batchInputs[cnt] = self.testset.data[s]
        batchLabels[cnt] = self.testset.label[s]
    end

    return batchInputs, batchLabels
end

return M.DataLoader