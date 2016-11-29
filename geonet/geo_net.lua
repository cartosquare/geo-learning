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

function M.toyNet(input_channels)
    net = nn.Sequential()
    -- 3x3 convolution kernel
    net:add(nn.SpatialConvolution(input_channels, input_channels * 3, 3, 3)) 
    net:add(nn.ReLU())                                      -- non-linearity 
    net:add(nn.SpatialMaxPooling(2,2,2,2))                  -- 2x2 windows max-pooling

    net:add(nn.View(input_channels * 3 * 3 * 3))            -- reshapes to flatten array
    net:add(nn.Linear(input_channels * 3 * 3 * 3, 120))     -- fully connected layer
    net:add(nn.ReLU())          -- non-linearity 

    net:add(nn.Linear(120, 84))
    net:add(nn.ReLU())          -- non-linearity 

    net:add(nn.Linear(84, 24))
    net:add(nn.ReLU())          -- non-linearity 

    net:add(nn.Linear(24, 1))   -- output size is 1
    return net
end

function M.linearNet(input_channels)
    net = nn.Sequential()

    net:add(nn.View(input_channels * 9 * 9))            -- reshapes to flatten array
    net:add(nn.Linear(input_channels * 9 * 9, 120))     -- fully connected layer
    net:add(nn.ReLU())          -- non-linearity 

    net:add(nn.Linear(120, 84))
    net:add(nn.ReLU())          -- non-linearity 

    net:add(nn.Linear(84, 24))
    net:add(nn.ReLU())          -- non-linearity 
    
    net:add(nn.Linear(24, 1))   -- output size is 1
    return net
end

return M