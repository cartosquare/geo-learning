--[[
/***************************************************************************
 train
                                 training/tesing script
 train and test
                              -------------------
        begin                : 2016-11-3
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
--]]

require 'torch'
require 'nn'
require 'math'

-- parse command line
local opts = require 'geonet/opts'
local opt = opts.parse(arg)

-- loading train/test sets
trainset = torch.load(opt.trainSet)
testset = torch.load(opt.testSet)

-- convert train/test sets as objects
setmetatable(trainset, 
    {__index = function(t, i) 
                    return {t.data[i], t.label[i]} 
                end}
);

function trainset:size() 
    return self.data:size(1) 
end


setmetatable(testset, 
    {__index = function(t, i) 
                    return {t.data[i], t.label[i]} 
                end}
);

function testset:size() 
    return self.data:size(1) 
end

-- summary
print('trainSet size: ', trainset:size())
print('testSet size: ', testset:size())

-- parse feature names
local nfeatures = trainset.data:size(2)
print('feature size: ', nfeatures)

-- normalize train/test: make data to have a mean of 0.0 and standard-deviation of 1.0
mean = {} -- store the mean, to normalize the test set in the future
stdv  = {} -- store the standard-deviation for the future
for i = 1, nfeatures do -- over each channel
    mean[i] = trainset.data[{ {}, {i}, {}, {}  }]:mean() -- mean estimation
    print('Channel ' .. i .. ', Mean: ' .. mean[i])
    trainset.data[{ {}, {i}, {}, {}  }]:add(-mean[i]) -- mean subtraction
    
    stdv[i] = trainset.data[{ {}, {i}, {}, {}  }]:std() -- std estimation
    print('Channel ' .. i .. ', Standard Deviation: ' .. stdv[i])
    trainset.data[{ {}, {i}, {}, {}  }]:div(stdv[i]) -- std scaling
end
-- the same operation to test set
for i = 1, nfeatures do -- over each channel
    testset.data[{ {}, {i}, {}, {}  }]:add(-mean[i]) -- mean subtraction    
    testset.data[{ {}, {i}, {}, {}  }]:div(stdv[i]) -- std scaling
end

-- normalize label
mean = trainset.label:mean()
print('Label mean ' .. mean)
trainset.label:add(-mean)
testset.label:add(-mean)

stdv = trainset.label:std()
print('Label stdv ' .. stdv)
trainset.label:div(stdv)
testset.label:div(stdv)

-- define neural network
local geo_net = require 'geonet/geo_net'
net = geo_net.linearNet(nfeatures)

-- define the loass function, use the Mean Squared Error criterion
criterion = nn.MSECriterion()

if opt.useGPU == 1 then
    require 'cunn'

    net = net:cuda()
    criterion = criterion:cuda()
    trainset.data = trainset.data:cuda()
    trainset.label = trainset.label:cuda()
    testset.data = testset.data:cuda()
    testset.label = testset.label:cuda()
end

-- train the neural network
trainer = nn.StochasticGradient(net, criterion)
trainer.learningRate = opt.LR
trainer.maxIteration = opt.nEpochs
trainer.learningRateDecay = opt.LRD

trainer:train(trainset)

torch.save('model.t7',net)

-- calculate MSE and MAPE errors
mse = 0
mape = 0
for i = 1, testset:size() do
    local groundtruth = testset.label[i]
    local prediction = net:forward(testset.data[i])
    mse = mse + (groundtruth[1] - prediction[1]) * (groundtruth[1] - prediction[1])
    mape = mape + math.abs(prediction[1] - groundtruth[1]) / groundtruth[1]
    print(groundtruth[1], prediction[1])
end

mse = mse / testset:size()
mape = mape / testset:size()
print('mse: ', mse)
print('mape: ', mape)