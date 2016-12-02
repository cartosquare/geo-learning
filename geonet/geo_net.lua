--[[
/***************************************************************************
 geo_net
                                 neural network defination
 define neural network for GeoLearning
                              -------------------
        begin                : 2016-11-3
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
--]]

local M = { }


function M.CNN(input_channels)
    net = nn.Sequential()
    -- 3x3 convolution kernel
    net:add(nn.SpatialConvolution(input_channels, input_channels * 3, 2, 2)) 
    net:add(nn.ReLU())                                      -- non-linearity 
    net:add(nn.SpatialMaxPooling(2,2,2,2))                  -- 2x2 windows max-pooling

    net:add(nn.SpatialConvolution(input_channels * 3, input_channels * 6, 2, 2)) 
    net:add(nn.ReLU())                                      -- non-linearity 
    net:add(nn.SpatialMaxPooling(2,2,2,2))                  -- 2x2 windows max-pooling

    net:add(nn.View(input_channels * 6 * 1 * 1))            -- reshapes to flatten array

    net:add(nn.Linear(input_channels * 6 * 1 * 1, input_channels * 6 * 1 * 1))     -- fully connected layer
    net:add(nn.BatchNormalization(input_channels * 6))
    net:add(nn.PReLU())          -- non-linearity 
    net:add(nn.Dropout(0.2))

    net:add(nn.Linear(input_channels * 6 * 1 * 1, input_channels * 6 * 1 * 1))
    net:add(nn.BatchNormalization(input_channels * 6))
    net:add(nn.PReLU())          -- non-linearity 
    net:add(nn.Dropout(0.2))

    net:add(nn.Linear(input_channels * 6 * 1 * 1, input_channels * 6 * 1 * 1))
    net:add(nn.BatchNormalization(input_channels * 6))
    net:add(nn.PReLU())          -- non-linearity 
    net:add(nn.Dropout(0.2))

    net:add(nn.Linear(input_channels * 6 * 1 * 1, 1))   -- output size is 1
    return net
end

function M.TurnCNN(input_channels, transfer_fun, dropout)
    net = nn.Sequential()
    -- 3x3 convolution kernel
    net:add(nn.SpatialConvolution(input_channels, input_channels * 3, 2, 2)) 
    net:add(nn.ReLU())                                      -- non-linearity 
    net:add(nn.SpatialMaxPooling(2,2,2,2))                  -- 2x2 windows max-pooling

    net:add(nn.SpatialConvolution(input_channels * 3, input_channels * 6, 2, 2)) 
    net:add(nn.ReLU())                                      -- non-linearity 
    net:add(nn.SpatialMaxPooling(2,2,2,2))                  -- 2x2 windows max-pooling

    net:add(nn.View(input_channels * 6 * 1 * 1))            -- reshapes to flatten array

    for i = 0, 2 do
        net:add(nn.Linear(input_channels * 6 * 1 * 1, input_channels * 6 * 1 * 1))
        -- transfer function:nn.HardTanh, nn.HardShrink, nn.SoftShrink, nn.SoftMax, nn.SoftMin, nn.SoftPlus, nn.SoftSign, nn.LogSigmoid, nn.LogSoftMax, nn.Sigmoid, nn.Tanh, nn.ReLU, nn.ReLU6, nn.PReLU, nn.RReLU, nn.ELU, nn.LeakyReLU
        if transfer_fun == 'HardTanh' then
            net:add(nn.HardTanh())
        elseif transfer_fun == 'HardShrink' then
            net:add(nn.HardShrink())
        elseif transfer_fun == 'SoftShrink' then
            net:add(nn.SoftShrink())
        elseif transfer_fun == 'SoftMax' then
            net:add(nn.SoftMax())
        elseif transfer_fun == 'SoftMin' then
            net:add(nn.SoftMin())
        elseif transfer_fun == 'SoftPlus' then
            net:add(nn.SoftPlus())
        elseif transfer_fun == 'SoftSign' then
            net:add(nn.SoftSign())
        elseif transfer_fun == 'LogSigmoid' then
            net:add(nn.LogSigmoid())
        elseif transfer_fun == 'LogSoftMax' then
            net:add(nn.LogSoftMax())
        elseif transfer_fun == 'Sigmoid' then
            net:add(nn.Sigmoid())
        elseif transfer_fun == 'Tanh' then
            net:add(nn.Tanh())
        elseif transfer_fun == 'ReLU' then
            net:add(nn.ReLU())
        elseif transfer_fun == 'ReLU6' then
            net:add(nn.ReLU6())
        elseif transfer_fun == 'PReLU' then
            net:add(nn.PReLU())
        elseif transfer_fun == 'RReLU' then
            net:add(nn.RReLU())
        elseif transfer_fun == 'ELU' then
            net:add(nn.ELU())
        elseif transfer_fun == 'LeakyReLU' then
            net:add(nn.LeakyReLU())
        else
            print('unknow transfer function' .. transfer_fun)
        end
        net:add(nn.Dropout(dropout))
    end

    net:add(nn.Linear(input_channels * 6 * 1 * 1, 1))   -- output size is 1
    return net
end

function M.toyNet(input_channels)
    net = nn.Sequential()
    -- 3x3 convolution kernel
    net:add(nn.SpatialConvolution(input_channels, input_channels * 3, 3, 3)) 
    net:add(nn.ReLU())                                      -- non-linearity 
    net:add(nn.SpatialMaxPooling(2,2,2,2))                  -- 2x2 windows max-pooling

    net:add(nn.View(input_channels * 3 * 3 * 3))            -- reshapes to flatten array
    net:add(nn.Linear(input_channels * 3 * 3 * 3, 120))     -- fully connected layer
    net:add(nn.ReLU())          -- non-linearity 
    net:add(nn.Dropout(0.5))

    net:add(nn.Linear(120, 84))
    net:add(nn.ReLU())          -- non-linearity 
    net:add(nn.Dropout(0.5))

    net:add(nn.Linear(84, 24))
    net:add(nn.ReLU())          -- non-linearity 
    net:add(nn.Dropout(0.5))

    net:add(nn.Linear(24, 1))   -- output size is 1
    return net
end

function M.linearNet(input_channels)
    net = nn.Sequential()

    net:add(nn.View(input_channels * 9 * 9))            -- reshapes to flatten array
    net:add(nn.Linear(input_channels * 9 * 9, input_channels * 9 * 9))     -- fully connected layer
    net:add(nn.ReLU())          -- non-linearity 
    
    net:add(nn.Linear(input_channels * 9 * 9, 1))   -- output size is 1
    return net
end

return M