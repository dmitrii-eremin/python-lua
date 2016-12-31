--[[
    Begin the lua pythonization.
--]]

local string_meta = getmetatable("")
string_meta.__add = function(v1, v2)
    if type(v1) == "string" and type(v2) == "string" then
        return v1 .. v2
    end
    return v1 + v2
end

local str = tostring
local int = tonumber

local function len(t)
    if type(t._data) == "table" then
        return #t._data
    end

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
    local result = {}

    result.is_list = true

    result._data = {}
    for _, v in ipairs(t) do
        table.insert(result._data, v)
    end
 
    local methods = {}

    methods.append = function(value)
        table.insert(result._data, value)
    end

    local iterator_index = nil

    setmetatable(result, {
        __index = function(self, index)
            if type(index) == "number" and index < 0 then
                return rawget(result._data, #result._data + index + 1)
            end

            return methods[index]
        end,
        __newindex = function(self, index, value)
            result._data[index] = value
        end,
        __call = function(self, _, idx)
            if idx == nil and iterator_index ~= nil then
                iterator_index = nil
            end

            local v = nil
            iterator_index, v = next(result._data, iterator_index)

            return v
        end,
    })

    return result
end

function dict(t)
    local result = {}

    result.is_dict = true

    result._data = {}
    for k, v in pairs(t) do
        result._data[k] = v
    end

    local methods = {}
    
    methods.items = function()
         return pairs(result._data)
    end

    local key_index = nil
    
    setmetatable(result, {
        __index = function(self, index)
            return methods[index]
        end,
        __newindex = function(self, index, value)
            result._data[index] = value
        end,
        __call = function(self, _, idx)
            if idx == nil and key_index ~= nil then
                key_index = nil
            end

            key_index, _ = next(result._data, key_index)

            return key_index
        end,
    })
    
    return result
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

local function staticmethod(old_fun)
    local wrapper = function(first, ...)
        return old_fun(...)
    end

    return wrapper
end

local function operator_in(item, items)
    if type(items) == "table" then
        for v in items do
            if v == item then
                return true
            end
        end
    elseif type(items) == "string" and type(item) == "string" then
        return string.find(items, item, 1, true) ~= nil
    end

    return false
end

-- Lua classes
local function class(class_init, bases)
    bases = bases or {}

    local c = {}
    
    for _, base in ipairs(bases) do
        for k, v in pairs(base) do
            c[k] = v
        end
    end

    c._bases = bases
    
    c = class_init(c)
    
    local mt = getmetatable(c) or {}
    mt.__call = function(_, ...)
        local object = {}
        
        setmetatable(object, {
            __index = function(tbl, idx)
                local method = c[idx]
                if type(method) == "function" then
                    return function(...)
                        return c[idx](object, ...) 
                    end
                end
                
                return method
            end,
        })
    
        if type(object.__init__) == "function" then
            object.__init__(...)
        end
        
        return object
    end
    
    setmetatable(c, mt)
    
    return c
end
--[[
    End of the lua pythonization.
--]]

