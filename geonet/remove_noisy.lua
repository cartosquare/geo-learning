require 'torch'
require 'nn'

local trainset = torch.load('geodata/poi_data/test_bj.t7')

local samples = trainset.label:size()[1]
local nfeatures = trainset.data:size()[2]
local width = trainset.data:size()[3]
local height = trainset.data:size()[4]

local cnt = 0
local bad_id = {}
for i = 1, samples do
    if trainset.label[i][1] >= 1000 then
        cnt = cnt + 1
        print(trainset.label[i][1])
        bad_id[cnt] = i
    end
end

print('total noisy ', cnt)
local new_samples = samples - cnt
local train_data = torch.DoubleTensor(new_samples, nfeatures, width, height)
local train_label = torch.DoubleTensor(new_samples, 1)

local new_cnt = 0
for i = 1, samples do
    if trainset.label[i][1] < 1000 then
        new_cnt = new_cnt + 1
        train_data[new_cnt] = trainset.data[i]
        train_label[new_cnt] = trainset.label[i]
    end
end

print('aha...', cnt, new_cnt, samples)
local trainset = {['data']=train_data, ['label']=train_label}
torch.save('geodata/poi_data/test_bj_filter.t7', trainset)

print(trainset)