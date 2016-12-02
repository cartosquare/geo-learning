require 'torch'
require 'nn'
require 'math'

local trainset = torch.load('geodata/poi_data/test_bj.t7')
local samples = trainset.label:size()[1]

for i = 1, samples do
    trainset.label[i][1] = math.log(trainset.label[i][1] + 1)

    if trainset.label[i][1] >= 5 or trainset.label[i][1] <= 1 then
        print(trainset.label[i][1])
    end
end

torch.save('geodata/poi_data/test_bj_log.t7', trainset)

print(trainset)