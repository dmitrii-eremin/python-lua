local string_meta = getmetatable("")
string_meta.__add = function(v1, v2)
    if type(v1) == "string" and type(v2) == "string" then
        return v1 .. v2
    end
    return v1 + v2
end

local function len(t)
    return #t
end

local function range(from, to, step)
    assert(from ~= nil)
    
    if to == nil then
        to = from
        from = 1        
    end
    
    if step == nil then
        step = to > from and 1 or -1
    end

    local i = from
    
    return function()
        ret = i
        if (step > 0 and i > to) or (step < 0 and i < to) then
            return nil
        end
        
        i = i + step
        return ret
    end
end

local function list(t)
    local methods = {}

    local iterator_index = nil

    setmetatable(t, {
        __index = methods,
        __call = function(self, _, idx)
            if idx == nil and iterator_index ~= nil then
                iterator_index = nil
            end

            local v = nil
            iterator_index, v = next(t, iterator_index)

            return v
        end,
    })
    return t
end

function dict(t)
    local methods = {}
    
    methods.items = function()
         return pairs(t)
    end

    local key_index = nil
    
    setmetatable(t, {
        __index = methods,
        __call = function(self, _, idx)
            if idx == nil and key_index ~= nil then
                key_index = nil
            end

            key_index, _ = next(t, key_index)

            return key_index
        end,
    })
    
    return t
end

function enumerate(t, start)
    start = start or 1

    local i, v = next(t, nil)
    return function()
        local index, value = i, v
        i, v = next(t, i)

        if index == nil then
            return nil
        end

        return index + start - 1, value
    end
end