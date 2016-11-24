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
    -- @input_channels input channels, 6 output channels, 3x3 convolution kernel
    net:add(nn.SpatialConvolution(input_channels, input_channels * 2, 3, 3)) 
    net:add(nn.ReLU())  -- non-linearity 
    --net:add(nn.SpatialMaxPooling(2,2,2,2))     -- A max-pooling operation that looks at 2x2 windows and finds the max.

    net:add(nn.SpatialConvolution(input_channels * 2, input_channels * 3, 3, 3))
    net:add(nn.ReLU())                       -- non-linearity 
    --net:add(nn.SpatialMaxPooling(2,2,2,2))

    net:add(nn.View(input_channels * 3 * 5 * 5))   -- reshapes from a 3D tensor of 16x5x5 into 1D tensor of 16*5*5
    net:add(nn.Linear(input_channels * 3 * 5 * 5, 120))    -- fully connected layer (matrix multiplication between input and weights)
    net:add(nn.ReLU())          -- non-linearity 
    net:add(nn.Linear(120, 84))
    net:add(nn.ReLU())          -- non-linearity 
    net:add(nn.Linear(84, 1))   -- output size is 1

    return net
end

return M