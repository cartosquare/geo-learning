local sqlite3 = require 'lsqlite3'
local torch = require 'torch'
local math = require 'math'

local pb = require 'pb'
local grid_data = require 'protoc/grid_data'


local src = 'data/supermarket'
local output = 'data/train.t7'
local train_file = 'train.txt'
local features = {'carservice', 'laundry'}
local buffer = 12

-- magic number
local grid_size = 256

-- open dbs
nfeat = 0
for k, v in ipairs(features) do
    local db_path = 'data/' .. v .. '.sqlite3'
    db = sqlite3.open(db_path)
    features[v] = db
    nfeat = nfeat + 1
end

-- open train list and write training data
-- train data size
samples = 0
for line in io.lines(train_file) do
    samples = samples + 1
end
-- output double tensor
train_data = torch.DoubleTensor(samples, nfeat, buffer * 2 + 1, buffer * 2 + 1)
train_label = torch.DoubleTensor(samples)

-- only used for reporting progress
grid_cnt = 0 
total_grids = samples * (2 * buffer + 1) * (2 * buffer + 1)
step = math.floor(total_grids/ 100)
if step == 0 then
    step = 1
end

-- loop for each sample
sample_cnt = 0
for line in io.lines(train_file) do
    sample_cnt = sample_cnt + 1

    -- split line/sample
    keys = {}
    cnt = 1
    for i in string.gmatch(line, "%S+") do
        keys[cnt] = i
        cnt = cnt + 1
    end
    z = keys[1]
    x = tonumber(keys[2])
    y = tonumber(keys[3])
    ix = tonumber(keys[4])
    iy = tonumber(keys[5])
    label = tonumber(keys[6])

    -- sample label
    train_label[cnt] = label

    -- global index of this sample
    ox = x * grid_size + ix
    oy = y * grid_size + iy

    -- nearby grids of this sample
    for i = -buffer, buffer do
        for j = -buffer, buffer do
            -- global index of nearby grid
            n_ox = ox + i
            n_oy = oy + j

            -- global/relative index
            n_x = math.floor(n_ox / grid_size)
            n_ix = n_ox % grid_size

            n_y = math.floor(n_oy / grid_size)
            n_iy = n_oy % grid_size

            -- grid id
            --print(n_ox, n_oy, n_x, n_y, n_ix, n_iy)
            gid = z .. '-' .. tostring(n_x) .. '-' .. tostring(n_y)
            -- print(gid)

            -- loop each feature
            feat_cnt = 0
            for k, v in ipairs(features) do
                val = 0.0
                for row in features[v]:nrows(string.format("SELECT DATA from feature WHERE ID = '%s'", gid)) do
                    local bin = row.DATA
                    local msg = grid_data.GridData():Parse(bin)
                    layer = msg.layers[1]
                    -- print(layer.name, layer.version)

                    -- CAUTION: lua index starts from 1, so we add 1 here!!!
                    idx = layer.keys[n_ix * grid_size + n_iy + 1]
                    val = layer.values[idx + 1]
                end
                
                feat_cnt = feat_cnt + 1
                -- add data cell
                -- print(sample_cnt, i + buffer + 1, feat_cnt, val)
                train_data[sample_cnt][feat_cnt][i + buffer + 1][i + buffer + 1] = val

            end -- for k, v in ipairs(features) do
            -- update progress
            grid_cnt = grid_cnt + 1
            if grid_cnt % step == 0 then
                print('Processed ', grid_cnt / total_grids)
            end
        end -- for j = -buffer, buffer do
    end -- for i = -buffer, buffer do
end -- for line in io.lines(train_file) do

-- save training data
td = {['data']=train_data, ['label']=train_label}
torch.save(output, td)

-- close dbs
for k, v in ipairs(features) do
    features[v]:close()
end

    


