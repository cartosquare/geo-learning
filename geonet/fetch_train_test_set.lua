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

local buffer = opt.buffer
local gridWidth = opt.gridWidth
local gridHeight = opt.gridHeight
local gridList = opt.gridList

local pb = require 'pb'
local grid_data = require 'geogrid/protoc/grid_data'

print(os.date("%Y-%m-%d %H:%M:%S"))
print(opt)

-- split feature names
local features = {}
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
local nfeat = 0
for k, v in ipairs(features) do
    local db_path = opt.featDir .. v .. '.sqlite3'
    print(db_path)
    db = sqlite3.open(db_path)
    features[v] = db
    nfeat = nfeat + 1
end
print('nfeatuers: ', nfeat)
print(features)

-- open train list and write training data
-- train data size
local samples = 0
for line in io.lines(opt.gridList) do
    samples = samples + 1
end

-- output double tensor
local train_num = math.floor(samples * 0.6)
local test_num = samples - train_num
print('#train, #test', train_num, test_num)

local train_data = torch.DoubleTensor(train_num, nfeat, buffer * 2 + 1, buffer * 2 + 1)
local train_label = torch.DoubleTensor(train_num, 1)
local test_data = torch.DoubleTensor(test_num, nfeat, buffer * 2 + 1, buffer * 2 + 1)
local test_label = torch.DoubleTensor(test_num, 1)

-- only used for reporting progress
local grid_cnt = 0 
local total_grids = samples * (2 * buffer + 1) * (2 * buffer + 1)
print('total grids', total_grids)
local step = math.floor(total_grids / 100)
if step == 0 then
    step = 1
end

-- loop for each sample
local floor = math.floor
local everyline = io.lines
local strmatch = string.gmatch

local sample_cnt = 0
for line in everyline(gridList) do
    sample_cnt = sample_cnt + 1
    print(sample_cnt)
    -- to cache features, because parse feature from protobuf format is the 
    -- bottle neck of our program!!!
    local feature_maps = {}

    -- split line/sample
    local keys = {}
    local key_cnt = 1
    for i in strmatch(line, "%S+") do
        keys[key_cnt] = i
        key_cnt = key_cnt + 1
    end

    local z = keys[1]
    local x = tonumber(keys[2])
    local y = tonumber(keys[3])
    local ix = tonumber(keys[4])
    local iy = tonumber(keys[5])
    local label = tonumber(keys[6])

    -- sample label
    if sample_cnt <= train_num then
        train_label[sample_cnt][1] = label
    else
        test_label[sample_cnt - train_num][1] = label
    end

    -- global index of this sample
    local ox = x * gridHeight + ix
    local oy = y * gridWidth + iy

    --local t2 = os.time()
    --local t3 = 0
    --local tk = 0
    -- nearby grids of this sample
    for i = -buffer, buffer do
        for j = -buffer, buffer do
            -- global index of nearby grid
            local n_ox = ox + i
            local n_oy = oy + j

            -- global/relative index
            local n_x = floor(n_ox / gridHeight)
            local n_ix = n_ox % gridHeight

            local n_y = floor(n_oy / gridWidth)
            local n_iy = n_oy % gridWidth

            -- grid id
            local gid = z .. '_' .. tostring(n_x) .. '_' .. tostring(n_y)

            -- loop each feature    
            for k, v in ipairs(features) do
                local feat_map_key = v .. '_' .. gid
                local val = 0.0
                if (feature_maps[feat_map_key] == nil) then
                    -- TODO: if no feature queried, for simple, here set the val to 0.
                    -- Maybe we should drop this sample?
                    for row in features[v]:nrows(string.format("SELECT DATA from feature WHERE ID = '%s'", gid)) do
                        local bin = row.DATA
                        local msg = grid_data.GridData():Parse(bin)
                        local layer = msg.layers[1]
                        -- cache this layer
                        feature_maps[feat_map_key] = layer

                        -- CAUTION: lua index starts from 1, so we add 1 here!!!
                        local idx = layer.keys[n_ix * gridHeight + n_iy + 1]
                        if (layer.values ~= nil) then
                            local feat_val = layer.values[idx + 1]
                            if (feat_val ~= nil) then
                                val = feat_val
                            end
                        end
                    end
                else
                    -- directly get layer from cache :)
                    local layer = feature_maps[feat_map_key]
                    -- CAUTION: lua index starts from 1, so we add 1 here!!!
                    local idx = layer.keys[n_ix * gridHeight + n_iy + 1]
                    if (layer.values ~= nil) then
                        local feat_val = layer.values[idx + 1]
                        if (feat_val ~= nil) then
                            val = feat_val
                        end
                    end
                end

                -- add data cell
                if sample_cnt <= train_num then
                    train_data[sample_cnt][k][i + buffer + 1][j + buffer + 1] = val
                else
                    test_data[sample_cnt - train_num][k][i + buffer + 1][j + buffer + 1] = val
                end
            end -- for k, v in ipairs(features) do
            -- update progress
            grid_cnt = grid_cnt + 1
            if grid_cnt % step == 0 then
                print(os.date("%Y-%m-%d %H:%M:%S"))
                print('Processed ', grid_cnt / total_grids)
            end
        end -- for j = -buffer, buffer do
    end -- for i = -buffer, buffer do
    --feature_maps = nil
end -- for line in everyline(gridList) do

-- save training data
local trainset = {['data']=train_data, ['label']=train_label}
local testset = {['data']=test_data, ['label']=test_label}
torch.save(opt.trainSet, trainset)
torch.save(opt.testSet, testset)

print(trainset)
print(testset)

-- close dbs
for k, v in ipairs(features) do
    features[v]:close()
end

    


