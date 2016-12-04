--[[
/***************************************************************************
 train
                                 training/tesing script
 The training loop and learning rate schedule
                              -------------------
        begin                : 2016-11-3
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
--]]

local optim = require 'optim'

local M = {}
local Trainer = torch.class('geonet.Trainer', M)

function Trainer:__init(model, criterion, opt)
   self.model = model
   self.criterion = criterion
   self.optimState = {
      learningRate = opt.LR,
      learningRateDecay = 0.0,
      momentum = opt.momentum,
      --nesterov = true,
      --dampening = 0.0,
      weightDecay = opt.weightDecay,
   }
   print('initial optimate state', self.optimState)
   self.opt = opt
   self.useGPU = opt.useGPU
   self.params, self.gradParams = model:getParameters()
end

function Trainer:train(epoch, dataloader)
   -- Trains the model for a single epoch
   self.optimState.learningRate = self:learningRate(epoch)
   --print('learningRate', self.optimState.learningRate)
   
   local timer = torch.Timer()

   local function feval()
      return self.criterion.output, self.gradParams
   end

   local trainSize = dataloader:trainSize()
   local mseSum, maeSum, mapeSum, lossSum = 0.0, 0.0, 0.0, 0.0
   local N = 0

   print('=> Training epoch # ' .. epoch)
   -- set the batch norm to training mode
   self.model:training()
   for nbatch = 1, trainSize do
      self.input, self.target = dataloader:trainBatch(nbatch)
      if self.useGPU == 1 then
        self.input = self.input:cuda()
        self.target = self.target:cuda()
     end

      local output = self.model:forward(self.input):float()
      local batchSize = output:size(1)
      local loss = self.criterion:forward(self.model.output, self.target)

      self.model:zeroGradParameters()
      self.criterion:backward(self.model.output, self.target)
      self.model:backward(self.input, self.criterion.gradInput)

      optim.sgd(feval, self.params, self.optimState)

      local mse, mae, mape = self:computeScore(output, self.target)
      mseSum = mseSum + mse * batchSize
      maeSum = maeSum + mae * batchSize
      mapeSum = mapeSum + mape * batchSize
      lossSum = lossSum + loss * batchSize

      N = N + batchSize

      print((' | Epoch: [%d][%d/%d]    Time %.3f  Err %1.4f  mse %7.3f  mae %7.3f mape %7.3f'):format(
         epoch, nbatch, trainSize, timer:time().real, loss, mse, mae, mape))

      -- check that the storage didn't get changed do to an unfortunate getParameters call
      assert(self.params:storage() == self.model:parameters()[1]:storage())

      timer:reset()
   end

   print((' * Finished epoch # %d     mse: %7.3f  mae: %7.3f mape: %7.3f loss: %7.3f\n'):format(
      epoch, mseSum / N, maeSum / N, mapeSum / N, lossSum / N))

   return mseSum / N, maeSum / N, mapeSum / N, lossSum / N
end

function Trainer:test(epoch, dataloader)
   local timer = torch.Timer()

   local testSize = dataloader:testSize()

   local mseSum, maeSum, mapeSum, lossSum = 0.0, 0.0, 0.0, 0.0
   local N = 0

   self.model:evaluate()
   for nbatch = 1, testSize do
      self.input, self.target = dataloader:validateBatch(nbatch)
      if self.useGPU == 1 then
        self.input = self.input:cuda()
        self.target = self.target:cuda()
     end

      local output = self.model:forward(self.input):float()
      local batchSize = output:size(1)
      local loss = self.criterion:forward(self.model.output, self.target)

      local mse, mae, mape = self:computeScore(output, self.target)
      mseSum = mseSum + mse * batchSize
      maeSum = maeSum + mae * batchSize
      mapeSum = mapeSum + mape * batchSize
      lossSum = lossSum + loss * batchSize

      N = N + batchSize

      print((' | Test: [%d][%d/%d]    Time %.3f  mse %7.3f mae %7.3f mape %7.3f loss %7.3f'):format(
         epoch, nbatch, testSize, timer:time().real, mseSum / N, maeSum / N, mapeSum / N, lossSum / N))

      timer:reset()
   end
   self.model:training()

   print((' * Finished epoch # %d     mse: %7.3f  mae: %7.3f mape: %7.3f\n'):format(
      epoch, mseSum / N, maeSum / N, mapeSum / N))

   return mseSum / N, maeSum / N, mapeSum / N
end


function Trainer:computeScore(output, target)
   local batchSize = output:size(1)
   e = 2.718281828459
   mse, mae, mape = 0.0, 0.0, 0.0
   for i = 1, batchSize do
        local predict = output[i][1]
        local groundtruth = target[i]

        --mse = mse + criterion:forward(predictions[i], batchLabels[i])
        mse = mse + (groundtruth - predict) * (groundtruth - predict)
        mae = mae + math.abs(math.pow(e, predict) - math.pow(e, groundtruth))
        mape = mape + math.abs(math.pow(e, predict) - math.pow(e, groundtruth)) / math.pow(e, groundtruth)
        --mape = mape + math.abs(prediction[1] - groundtruth[1]) / groundtruth[1]
    end
    return mse / batchSize, mae / batchSize, mape / batchSize
end

function Trainer:learningRate(epoch)
   -- Training schedule
   local decay = 0.0
   decay = math.floor((epoch - 1) / 30)

   return self.opt.LR * math.pow(0.1, decay)
end

return M.Trainer
