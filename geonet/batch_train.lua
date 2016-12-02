--[[
/***************************************************************************
 train
                                 training/tesing script
 train and test
                              -------------------
        begin                : 2016-12-02
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
--]]

require 'torch'
require 'nn'
require 'optim'
require 'math'

-- parse command line
local opts = require 'geonet/opts'
local opt = opts.parse(arg)

-- loading train/test sets
trainset = torch.load(opt.trainSet)
testset = torch.load(opt.testSet)

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

-- define neural network
local geo_net = require 'geonet/geo_net'
net = geo_net.CNN(nfeatures)

-- define the loass function, use the Mean Squared Error criterion
criterion = nn.MSECriterion()

if opt.useGPU == 1 then
    require 'cunn'

    net = net:cuda()
    criterion = criterion:cuda()
end


-- train the neural network
params, gradParams = net:getParameters()
local optmState = {
    learningRate = opt.LR, 
    learningRateDecay = opt.LRD, 
    momentum = opt.momentum
    }
print(optmState)

local nbatchs = math.ceil(trainset.data:size(1) / opt.batchSize)
print('nbatchs', nbatchs)

local batchSize = opt.batchSize
local recent_error = 100
local no_good_cnt = 0
for epoch = 0, opt.nEpochs do
    local avg_loss = 0 
    for batch = 1, nbatchs do
        start_idx = batchSize * (batch - 1) + 1
        end_idx = batchSize * batch

        if end_idx > trainset.data:size(1) then
            end_idx = trainset.data:size(1)
            --print('reduce end index to ', end_idx)
        end

        batchInputs = torch.DoubleTensor(batchSize, nfeatures, 9, 9)
        batchLabels = torch.DoubleTensor(batchSize)
        local cnt = 0
        for s = start_idx, end_idx do
            cnt = cnt + 1

            batchInputs[cnt] = trainset.data[s]
            batchLabels[cnt] = trainset.label[s]
        end
        if cnt < batchSize then
            nremained = batchSize - cnt
            for ss = 1, nremained do
                cnt = cnt + 1

                batchInputs[cnt] = trainset.data[ss]
                batchLabels[cnt] = trainset.label[ss]
            end
        end
        if cnt ~= batchSize then
            print 'Inconsistent mini-batch!'
        end

        if opt.useGPU == 1 then
            batchInputs = batchInputs:cuda()
            batchLabels = batchLabels:cuda()
        end

        function feval(params)
            gradParams:zero()
        
            local outputs = net:forward(batchInputs)
            local loss = criterion:forward(outputs, batchLabels)
            local dloss_doutputs = criterion:backward(outputs, batchLabels)
            net:backward(batchInputs, dloss_doutputs)
            
            avg_loss = avg_loss + loss
            return loss, gradParams
        end
        optim.sgd(feval, params, optimState)
    end

    current_error = avg_loss / nbatchs
    if current_error < recent_error then
        recent_error = current_error
        no_good_cnt = 0
        print(string.format('after %d epchos, new best result J(x) = %f *', epoch, current_error))
    else
        no_good_cnt = no_good_cnt + 1
        print(string.format('after %d epchos, J(x) = %f', epoch, current_error))
    end
    
    if no_good_cnt > 10 then
        break
    end
end

-- calculate MSE and MAPE errors
mse = 0
mae = 0
mape = 0
e = 2.718281828459

ntests = testset.data:size(1)

local nbatchs_test = math.ceil(testset.data:size(1) / batchSize)
print('#test batchs', nbatchs_test)

for batch = 1, nbatchs_test do
    start_idx = batchSize * (batch - 1) + 1
    end_idx = batchSize * batch

    if end_idx > testset.data:size(1) then
        end_idx = testset.data:size(1)
    end

    batchInputs = torch.DoubleTensor(end_idx - start_idx + 1, nfeatures, 9, 9)
    batchLabels = torch.DoubleTensor(end_idx - start_idx + 1)

    local cnt = 0
    for s = start_idx, end_idx do
        cnt = cnt + 1

        batchInputs[cnt] = testset.data[s]
        batchLabels[cnt] = testset.label[s]
    end

    if opt.useGPU == 1 then
        batchInputs = batchInputs:cuda()
        batchLabels = batchLabels:cuda()
    end

    local predictions = net:forward(batchInputs)
    for i = 1,cnt do
        local predict = predictions[i][1]
        local groundtruth = batchLabels[i]

        --mse = mse + criterion:forward(predictions[i], batchLabels[i])
        mse = mse + (groundtruth - predict) * (groundtruth - predict)
        mae = mae + math.abs(math.pow(e, predict) - math.pow(e, groundtruth))
        mape = mape + math.abs(math.pow(e, predict) - math.pow(e, groundtruth)) / math.pow(e, groundtruth)
        --mape = mape + math.abs(prediction[1] - groundtruth[1]) / groundtruth[1]
        if i % 50 == 0 then
            print(math.pow(e, groundtruth), math.pow(e, predict))
            --print(groundtruth[1], prediction[1])
        end
    end
end

mse = mse / ntests
mae = mae / ntests
mape = mape / ntests

print('mse: ', mse)
print('mae: ', mae)
print('mape: ', mape)