--[[
/***************************************************************************
 main
                                 training script
 training entry
                              -------------------
        begin                : 2016-11-3
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
--]]

require 'torch'
require 'paths'
require 'optim'
require 'nn'

local DataLoader = require 'geonet/dataloader'
local Trainer = require 'geonet/train'
local opts = require 'geonet/opts'

local opt = opts.parse(arg)
torch.manualSeed(opt.manualSeed)

-- Data loading
local dataloader = DataLoader(opt)
dataloader:normalize()

-- Create model
-- define neural network
local geo_net = require 'geonet/geo_net'
model = geo_net.linearNet(dataloader.nfeatures)
for i,module in ipairs(model:listModules()) do
   print(module)
end

-- define the loass function, use the Mean Squared Error criterion
criterion = nn.MSECriterion()

if opt.useGPU == 1 then
    require 'cunn'

    model = model:cuda()
    criterion = criterion:cuda()
end

-- The trainer handles the training loop and evaluation on validation set
local trainer = Trainer(model, criterion, opt)

if opt.testOnly then
   local mse, mae, mape = trainer:test(0, dataloader)
   print(string.format(' * Results mse: %6.3f  mae: %6.3f mape: %6.3f', mse, mae, mape))
   return
end

local startEpoch = 1
local bestMse = math.huge
local bestMae = math.huge
local bestMape = math.huge
local trace_info = {['train'] = {}, ['test']= {}}
local no_improve_cnt = 0
logger = optim.Logger('error.log')
logger:setNames{'Training err.', 'Test err.'}

for epoch = startEpoch, opt.nEpochs do
   -- Train for a single epoch
   local mse, mae, mape, trainLoss = trainer:train(epoch, dataloader)
   
   -- Run model on validation set
   local testMse, testMae, testMape = trainer:test(epoch, dataloader)

   trace_info['train'][epoch] = mse
   trace_info['test'][epoch] = testMse

   logger:add{mse, testMse}
   logger:style{'+-', '+-'}
   logger:plot()

   local bestModel = false
   if testMse < bestMse then
      bestModel = true
      bestMse = testMse
      bestMae = testMae
      bestMape = testMape
      print(' * Best model ', testMse, testMae, testMape)
   end

   if bestModel then
        --torch.save('best.t7', model)
        no_improve_cnt = 0
   else
        no_improve_cnt = no_improve_cnt + 1
   end
   
   if no_improve_cnt > 10 then
        print('not improve 10 epochs .... break ...')
        break
   end
end

print(string.format(' * Finished mse: %6.3f  mae: %6.3f  mape: %6.3f', bestMse, bestMae, bestMape))
torch.save('trace_info.t7', trace_info)