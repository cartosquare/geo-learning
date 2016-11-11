--[[
/***************************************************************************
 fetch_train_test_set
                                 fetch traing/testing set
 from grid list to torch7 format training/testing data
                              -------------------
        begin                : 2016-11-3
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
--]]

local sqlite3 = require 'lsqlite3'
local torch = require 'torch'
local math = require 'math'

-- parse command line
local opts = require 'geonet/opts'
local opt = opts.parse(arg)

local pb = require 'pb'
local grid_data = require 'geogrid/protoc/grid_data'

print(os.date("%Y-%m-%d %H:%M:%S"))
print(opt)

-- split feature names
local features = {}
keys = {}
local feat_cnt = 0
for feat in string.gmatch(opt.features, "%S+") do
    feat_cnt = feat_cnt + 1
    features[feat_cnt] = feat
end

-- do some check
if feat_cnt == 0 then
    print('feature name is required!')
    return
end


-- open feature dbs
nfeat = 0
for k, v in ipairs(features) do
    local db_path = opt.featDir .. v .. '.sqlite3'
    db = sqlite3.open(db_path)
    features[v] = db
    nfeat = nfeat + 1
end
print('nfeatuers: ', nfeat)

-- open train list and write training data
-- train data size
samples = 0
for line in io.lines(opt.gridList) do
    samples = samples + 1
end

-- output double tensor
train_num = math.floor(samples * 0.6)
test_num = samples - train_num
print(train_num,  test_num)

train_data = torch.DoubleTensor(train_num, nfeat, opt.buffer * 2 + 1, opt.buffer * 2 + 1)
train_label = torch.DoubleTensor(train_num, 1)
test_data = torch.DoubleTensor(test_num, nfeat, opt.buffer * 2 + 1, opt.buffer * 2 + 1)
test_label = torch.DoubleTensor(test_num, 1)

-- only used for reporting progress
grid_cnt = 0 
total_grids = samples * (2 * opt.buffer + 1) * (2 * opt.buffer + 1)
print('total grids', total_grids)
step = math.floor(total_grids/ 100)
if step == 0 then
    step = 1
end

-- loop for each sample
sample_cnt = 0
for line in io.lines(opt.gridList) do
    sample_cnt = sample_cnt + 1
    print(sample_cnt)

    -- split line/sample
    keys = {}
    local key_cnt = 1
    for i in string.gmatch(line, "%S+") do
        keys[key_cnt] = i
        key_cnt = key_cnt + 1
    end
    z = keys[1]
    x = tonumber(keys[2])
    y = tonumber(keys[3])
    ix = tonumber(keys[4])
    iy = tonumber(keys[5])
    label = tonumber(keys[6])

    -- sample label
    if sample_cnt <= train_num then
        train_label[sample_cnt][1] = label
    else
        test_label[sample_cnt - train_num][1] = label
    end

    -- global index of this sample
    ox = x * opt.gridSize + ix
    oy = y * opt.gridSize + iy

    -- nearby grids of this sample
    for i = -opt.buffer, opt.buffer do
        for j = -opt.buffer, opt.buffer do
            -- global index of nearby grid
            n_ox = ox + i
            n_oy = oy + j

            -- global/relative index
            n_x = math.floor(n_ox / opt.gridSize)
            n_ix = n_ox % opt.gridSize

            n_y = math.floor(n_oy / opt.gridSize)
            n_iy = n_oy % opt.gridSize

            -- grid id
            gid = z .. '-' .. tostring(n_x) .. '-' .. tostring(n_y)

            -- loop each feature
            for k, v in ipairs(features) do
                val = 0.0
                -- TODO: if no feature queried, for simple, here set the val to 0.
                -- Maybe we should drop this sample?
                for row in features[v]:nrows(string.format("SELECT DATA from feature WHERE ID = '%s'", gid)) do
                    if (row ~= nil) then
                        local bin = row.DATA
                        local msg = grid_data.GridData():Parse(bin)
                        layer = msg.layers[1]

                        -- CAUTION: lua index starts from 1, so we add 1 here!!!
                        idx = layer.keys[n_ix * opt.gridSize + n_iy + 1]
                        if (layer.values[idx + 1] ~= nil) then
                            val = layer.values[idx + 1]
                        end
                    end
                end

                -- add data cell
                if sample_cnt <= train_num then
                    train_data[sample_cnt][k][i + opt.buffer + 1][j + opt.buffer + 1] = val
                else
                    
                    test_data[sample_cnt - train_num][k][i + opt.buffer + 1][j + opt.buffer + 1] = val
                end
            end -- for k, v in ipairs(features) do

            -- update progress
            grid_cnt = grid_cnt + 1
            if grid_cnt % step == 0 then
                print(os.date("%Y-%m-%d %H:%M:%S"))
                print('Processed ', grid_cnt / total_grids)
            end
        end -- for j = -opt.buffer, opt.buffer do
    end -- for i = -opt.buffer, opt.buffer do
end -- for line in io.lines(opt.gridList) do

-- save training data
trainset = {['data']=train_data, ['label']=train_label}
testset = {['data']=test_data, ['label']=test_label}
torch.save(opt.trainSet, trainset)
torch.save(opt.testSet, testset)

print(trainset)
print(testset)

-- close dbs
for k, v in ipairs(features) do
    features[v]:close()
end

    


