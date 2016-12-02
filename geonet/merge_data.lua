require 'torch'
require 'nn'

local trainset1 = torch.load('geodata/poi_data/train_cc.t7')
local testset1 = torch.load('geodata/poi_data/test_cc.t7')

local trainset2 = torch.load('geodata/poi_data/train_dd.t7')
local testset2 = torch.load('geodata/poi_data/test_dd.t7')

print('trainset 1 size', trainset1.data:size(), trainset1.label:size())
print('trainset 2 size', trainset2.data:size(), trainset2.label:size())

local train_samples1 = trainset1.data:size()[1]
local train_samples2 = trainset2.data:size()[1]

local test_samples1 = testset1.data:size()[1]
local test_samples2 = testset2.data:size()[1]

local nfeatures = trainset1.data:size()[2]
local width = trainset1.data:size()[3]
local height = trainset1.data:size()[4]

-- allocate tensors
local train_data = torch.DoubleTensor(train_samples1 + train_samples2, nfeatures, width, height)
local train_label = torch.DoubleTensor(train_samples1 + train_samples2, 1)
print('train data allocated')

local test_data = torch.DoubleTensor(test_samples1 + test_samples2, nfeatures, width, height)
local test_label = torch.DoubleTensor(test_samples1 + test_samples2, 1)
print('test data allocated')

--[[
-- fill training tensors
for i = 1, train_samples1 do
    train_data[i] = trainset1.data[i]
    --trainset1.data[i] = nil
    train_label[i] = trainset1.label[i]
    --trainset1.label[i] = nil
end
print('train data part1')
for i = 1, train_samples2 do
    train_data[i + train_samples1] = trainset2.data[i]
    train_label[i + train_samples1] = trainset2.label[i]
end
print('train data part2')
local trainset = {['data']=train_data, ['label']=train_label}
torch.save('geodata/poi_data/train_bj.t7', trainset)

print(trainset)
trainset = nil
--]]
-- fill testing tensors
for i = 1, test_samples1 do
    test_data[i] = testset1.data[i]
    test_label[i] = testset1.label[i]
end
print('test data part1')
for i = 1, test_samples2 do
    test_data[i + test_samples1] = testset2.data[i]
    test_label[i + test_samples1] = testset2.label[i]
end
print('test data part1')
-- save training data

local testset = {['data']=test_data, ['label']=test_label}
torch.save('geodata/poi_data/test_bj.t7', testset)
print(testset)